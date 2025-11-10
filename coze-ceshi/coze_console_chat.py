import requests
import json

# ================== 配置信息 ==================
API_URL = "https://api.coze.cn/v3/chat"
BOT_ID = "7570913956290969651"  # 你的智能体 ID
TOKEN = "sat_xnzoVs4b3IGgoVxqg9Ezoxuep3UzYExc9GsZGqNePw1GYEc5th5oZuXo226MlNgJ"
USER_ID = "test_console_user"
# =============================================

def chat_with_coze(message: str):
    """
    调用 Coze Chat API (流式模式) 并实时打印回复
    """
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": True,               # ✅ 开启流式响应
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "type": "question",
                "content_type": "text",
                "content": message
            }
        ]
    }

    print("\n📤 正在请求 Coze 智能体 (流式)...\n")

    finished = False
    chunk_buffer: list[str] = []

    def flush_buffer(force: bool = False):
        if not chunk_buffer:
            return
        text = "".join(chunk_buffer)
        print(text, end="", flush=True)
        chunk_buffer.clear()

    def handle_event(event_type: str, data_payload: str):
        nonlocal finished
        if data_payload.strip() == "[DONE]":
            return
        try:
            parsed = json.loads(data_payload)
        except json.JSONDecodeError:
            return
        data_node = parsed.get("data") if isinstance(parsed, dict) else None
        if not data_node and isinstance(parsed, dict):
            data_node = parsed
        if event_type == "conversation.message.delta":
            text = None
            if isinstance(data_node, dict):
                text = data_node.get("content") or data_node.get("text")
            if text:
                chunk_buffer.append(text)
                if text.endswith(("\n", "。", ".", "!", "！", "?", "？")) or len("".join(chunk_buffer)) >= 200:
                    flush_buffer()
        elif event_type == "conversation.chat.completed":
            flush_buffer(force=True)
            print("\n\n✅ 对话完成！\n")
            finished = True

    try:
        with requests.post(API_URL, headers=headers, json=payload, stream=True) as resp:
            if resp.status_code != 200:
                print(f"❌ 请求失败：HTTP {resp.status_code}")
                print(resp.text)
                return

            current_event = ""
            buffer_data = ""

            for raw_line in resp.iter_lines(decode_unicode=False):
                if raw_line is None:
                    continue
                try:
                    line = raw_line.decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue

                if not line:
                    if current_event and buffer_data:
                        handle_event(current_event, buffer_data)
                    current_event = ""
                    buffer_data = ""
                    if finished:
                        return
                    continue

                if line.startswith("event:"):
                    current_event = line.split("event:", 1)[1].strip()
                    if current_event == "done":
                        finished = True
                    continue

                if line.startswith("data:"):
                    fragment = line.split("data:", 1)[1].strip()
                    buffer_data = f"{buffer_data}\n{fragment}".strip()
                    continue

                # 忽略其他字段（例如 id:）
                continue

            if current_event and buffer_data and not finished:
                handle_event(current_event, buffer_data)

    except Exception as e:
        print(f"❌ 调用异常：{e}")


if __name__ == "__main__":
    print("=== 🧠 连词成段 智能体测试 (Poetry 环境) ===")
    print("提示：输入 exit 退出\n")

    while True:
        user_input = input("请输入20个英文单词（或输入 exit 退出）：\n> ").strip()
        if user_input.lower() == "exit":
            print("👋 已退出程序。")
            break
        elif not user_input:
            continue

        chat_with_coze(user_input)
