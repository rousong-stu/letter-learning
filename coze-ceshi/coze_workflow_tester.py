"""
Coze Workflow 集成测试脚本
===========================

该脚本会自动从当前 MySQL 数据库读取指定用户的学习计划：
    - USER_CLASS  ← 计划中的学习课程字段（course_code）
    - USER_ENGLISH_LEVEL ← 计划关联的单词书名称
    - USER_TARGETWORD_NUM ← 计划的每日学习词数
    - 输入单词列表 ← 计划当日（或指定日）的单词列表

随后调用 Coze 工作流（workflow_id=7572622349360758824），打印生成的短文，
并把返回的插图保存到 `coze-ceshi/workflow_images` 目录下。

运行示例：
    poetry run python coze-ceshi/coze_workflow_tester.py --username ceshi09
    （可选）--day-index 2  指定学习的 Day 序号
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
from typing import Iterable, Sequence
from urllib.parse import urlparse

import httpx
import pymysql

API_URL = "https://api.coze.cn/v1/workflows/chat"
WORKFLOW_ID = "7572622349360758824"
SERVICE_IDENTITY_TOKEN = (
    "sat_xnzoVs4b3IGgoVxqg9Ezoxuep3UzYExc9GsZGqNePw1GYEc5th5oZuXo226MlNgJ"
)

# 数据库配置取自 backend/.env
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "letter_learning",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

COURSE_LABEL_MAP = {
    "basic": "基础巩固班",
    "postgraduate": "考研冲刺班",
    "toefl": "托福强化班",
    "ielts": "雅思口语班",
}

IMAGES_DIR = Path(__file__).resolve().parent / "workflow_images"


@dataclass
class PlanContext:
    user_id: int
    username: str
    plan_id: int
    course_label: str
    book_title: str
    daily_quota: int
    start_date: date
    total_days: int
    day_index: int
    words: list[str]


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def calc_day_index(start_date: date, total_days: int, override: int | None) -> int:
    if override:
        limit = total_days or override
        return max(1, min(limit, override))
    today = date.today()
    if start_date > today:
        return 1
    offset = (today - start_date).days
    day_idx = offset + 1
    return max(1, min(total_days or 1, day_idx))


def fetch_plan(username: str, day_override: int | None) -> PlanContext:
    sql_plan = """
        SELECT
            u.id AS user_id,
            u.username,
            uwb.id AS plan_id,
            uwb.course_code,
            uwb.daily_quota,
            uwb.start_date,
            uwb.total_days,
            wb.title AS book_title
        FROM users u
        JOIN user_word_books uwb ON uwb.user_id = u.id
        JOIN word_books wb ON wb.id = uwb.word_book_id
        WHERE u.username = %s
        ORDER BY uwb.created_at DESC
        LIMIT 1
    """
    sql_words = """
        SELECT wbw.word
        FROM user_word_book_words uwbw
        JOIN word_book_words wbw ON wbw.id = uwbw.word_book_word_id
        WHERE uwbw.user_word_book_id = %s AND uwbw.day_index = %s
        ORDER BY uwbw.sequence_in_day ASC, wbw.id ASC
    """
    sql_words_fallback = """
        SELECT wbw.word
        FROM user_word_book_words uwbw
        JOIN word_book_words wbw ON wbw.id = uwbw.word_book_word_id
        WHERE uwbw.user_word_book_id = %s
        ORDER BY uwbw.day_index ASC, uwbw.sequence_in_day ASC, wbw.id ASC
        LIMIT %s
    """
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(sql_plan, (username,))
        row = cursor.fetchone()
        if not row:
            raise RuntimeError(f"未找到用户 {username} 的学习计划，请先在系统中配置。")

        course_label = COURSE_LABEL_MAP.get(
            row["course_code"], row["course_code"] or "未设置课程"
        )
        day_index = calc_day_index(
            row["start_date"], row["total_days"], day_override
        )

        cursor.execute(sql_words, (row["plan_id"], day_index))
        words = [w["word"] for w in cursor.fetchall() if w.get("word")]
        if not words:
            cursor.execute(
                sql_words_fallback, (row["plan_id"], row["daily_quota"])
            )
            words = [w["word"] for w in cursor.fetchall() if w.get("word")]

        if not words:
            raise RuntimeError("未获取到任何单词，请确认单词书已导入。")

    return PlanContext(
        user_id=row["user_id"],
        username=row["username"],
        plan_id=row["plan_id"],
        course_label=course_label,
        book_title=row["book_title"],
        daily_quota=row["daily_quota"],
        start_date=row["start_date"],
        total_days=row["total_days"],
        day_index=day_index,
        words=words,
    )


def normalize_text_from_block(block: dict) -> str:
    if not isinstance(block, dict):
        return ""
    if block.get("type") == "text":
        return block.get("text") or block.get("content") or ""
    if block.get("type") == "raw_text":
        return block.get("text") or ""
    return ""


def extract_text_from_event(data_node: dict) -> str:
    if not isinstance(data_node, dict):
        return ""
    content = data_node.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = [normalize_text_from_block(block) for block in content]
        return "".join(filter(None, texts))
    if isinstance(content, dict) and isinstance(content.get("content"), list):
        texts = [normalize_text_from_block(b) for b in content["content"]]
        return "".join(filter(None, texts))
    # 某些事件使用 data["text"]
    return data_node.get("text") or ""


def extract_image_urls(event_payload: dict) -> list[str]:
    """按照文档建议解析图片 URL。"""

    def _extract(blocks: Iterable[dict]) -> list[str]:
        urls: list[str] = []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "image" and isinstance(
                block.get("image"), dict
            ):
                url = block["image"].get("url")
                if url:
                    urls.append(url)
            elif block.get("type") == "images":
                for img in block.get("images") or []:
                    if isinstance(img, dict):
                        url = img.get("url")
                        if url:
                            urls.append(url)
        return urls

    data = event_payload.get("data") or event_payload
    content = data.get("content")
    if isinstance(content, list):
        return _extract(content)
    if isinstance(content, dict) and isinstance(content.get("content"), list):
        return _extract(content["content"])
    if isinstance(data.get("images"), Sequence):
        return [
            img.get("url")
            for img in data["images"]
            if isinstance(img, dict) and img.get("url")
        ]
    return []


def split_story_sections(full_text: str) -> tuple[str, str]:
    label_story = "英文短文："
    label_image = "根据短文自动生成的插图："
    text = full_text.strip()
    if text.startswith(label_story):
        text = text[len(label_story) :].strip()
    image_caption = ""
    idx = text.find(label_image)
    if idx != -1:
        story = text[:idx].strip()
        image_caption = text[idx + len(label_image) :].strip()
    else:
        story = text.strip()
    return story, image_caption


def download_images(urls: Sequence[str]) -> list[Path]:
    saved_paths: list[Path] = []
    if not urls:
        return saved_paths
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for idx, url in enumerate(urls, start=1):
            try:
                resp = client.get(url)
                resp.raise_for_status()
                extension = Path(urlparse(url).path).suffix or ".png"
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = (
                    IMAGES_DIR / f"workflow_image_{timestamp}_{idx}{extension}"
                )
                with open(filename, "wb") as fh:
                    fh.write(resp.content)
                saved_paths.append(filename)
            except Exception as exc:  # noqa: BLE001
                print(f"⚠️  下载图片失败: {url}，错误：{exc}")
    return saved_paths


def call_workflow(
    *,
    user_input: str,
    user_class: str,
    english_level: str,
    target_word_num: int,
    debug: bool = False,
) -> tuple[str, list[str]]:
    headers = {
        "Authorization": f"Bearer {SERVICE_IDENTITY_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "workflow_id": WORKFLOW_ID,
        "stream": True,
        "additional_messages": [
            {
                "role": "user",
                "type": "question",
                "content_type": "text",
                "content": user_input,
            }
        ],
        "parameters": {
            "CONVERSATION_NAME": "LetterLearning Auto",
            "USER_CLASS": user_class,
            "USER_ENGLISH_LEVEL": english_level,
            "USER_TARGETWORD_NUM": str(target_word_num),
        },
    }

    chunks: list[str] = []
    image_urls: list[str] = []

    def process_event(event: dict):
        nonlocal chunks, image_urls
        if not isinstance(event, dict):
            return
        event_type = event.get("event") or ""
        data_node = event.get("data") or event
        if debug:
            print(f"\n[debug] event={event_type} data={event.get('data')}")
        text = ""
        if event_type == "conversation.message.delta":
            text = extract_text_from_event(data_node)
        elif event_type == "conversation.message.completed" and not chunks:
            text = extract_text_from_event(data_node)
        elif not event_type:
            text = extract_text_from_event(data_node)
        if text:
            if debug:
                print(f"[debug] text chunk: {text}")
            chunks.append(text)
        urls = extract_image_urls(event)
        if urls:
            image_urls.extend(urls)

    with httpx.stream(
        "POST", API_URL, headers=headers, json=payload, timeout=180
    ) as resp:
        resp.raise_for_status()
        current_event = ""
        buffer_data = ""
        for raw_line in resp.iter_lines():
            if raw_line is None:
                continue
            line = raw_line.strip()
            if debug and line:
                print(f"\n[debug] raw line: {line}")
            if not line:
                if current_event and buffer_data:
                    payload = buffer_data.strip()
                    if payload and payload != "[DONE]":
                        try:
                            event = json.loads(payload)
                        except json.JSONDecodeError:
                            event = None
                        else:
                            event.setdefault("event", current_event)
                        if event:
                            process_event(event)
                current_event = ""
                buffer_data = ""
                continue
            if line.startswith("{") or line.startswith("["):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                process_event(event)
                continue
            if line.startswith("event:"):
                current_event = line.split("event:", 1)[1].strip()
                continue
            if line.startswith("data:"):
                fragment = line.split("data:", 1)[1].strip()
                buffer_data = f"{buffer_data}\n{fragment}".strip()
                continue

    print("\n\n✅ 工作流调用完成\n")
    unique_urls = list(dict.fromkeys(image_urls))
    return "".join(chunks), unique_urls


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Coze Workflow（Syntexia）调试脚本"
    )
    parser.add_argument(
        "--username",
        required=True,
        help="系统中的用户名，将读取该用户当前的学习计划",
    )
    parser.add_argument(
        "--day-index",
        type=int,
        default=None,
        help="可选，指定学习 Day 序号（默认按开始日期推算今日）",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="输出原始事件，便于排查",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = fetch_plan(args.username, args.day_index)
    words_str = ", ".join(plan.words[: plan.daily_quota])

    print(
        f"👤 用户：{plan.username}（ID={plan.user_id}）\n"
        f"📚 单词书：{plan.book_title}\n"
        f"🎯 学习课程：{plan.course_label}\n"
        f"📆 Day {plan.day_index}（开始日期：{plan.start_date}）\n"
        f"🔢 每日词数：{plan.daily_quota}\n"
        f"📝 本次发送的单词：{words_str}"
    )
    print("\n🚀 正在调用 Coze 工作流...\n")

    raw_text, image_urls = call_workflow(
        user_input=words_str,
        user_class=plan.course_label,
        english_level=plan.book_title,
        target_word_num=plan.daily_quota,
        debug=args.debug,
    )

    story, image_caption = split_story_sections(raw_text)
    if not image_urls and image_caption:
        url_candidates = re.findall(r"https?://[^\s]+", image_caption)
        image_urls.extend(url_candidates)
    print("------ 英文短文 ------")
    print(story or "(未解析到短文内容)")
    print("\n------ 插图说明 ------")
    print(image_caption or "(未解析到插图描述)")

    saved_paths = download_images(image_urls)
    if saved_paths:
        print("\n🖼️  图片已保存至：")
        for path in saved_paths:
            print(f" - {path}")
    else:
        print("\n⚠️  未获取到图片 URL。")


if __name__ == "__main__":
    main()
