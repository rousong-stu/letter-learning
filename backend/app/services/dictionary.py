from __future__ import annotations

import html
import logging
import re
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import DictionaryEntry
from app.schemas.dictionary import DictionaryEntryResponse, DefinitionSchema
from app.repositories import dictionary as dictionary_repo

logger = logging.getLogger(__name__)
settings = get_settings()

DICTIONARY_ENDPOINT = (
    "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
)
THESAURUS_ENDPOINT = (
    "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/"
)
TOKEN_PATTERN = re.compile(r"\{[^}]+\}")


class DictionaryLookupError(RuntimeError):
    """通用词典查询错误。"""


class DictionaryEntryNotFound(DictionaryLookupError):
    """词典未找到指定单词。"""


def _normalize_word(raw_word: str) -> tuple[str, str]:
    original = raw_word.strip()
    if not original:
        raise ValueError("请输入有效的英文单词")
    normalized = re.sub(r"\s+", " ", original).lower()
    return original, normalized


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    cleaned = TOKEN_PATTERN.sub("", value)
    return html.unescape(cleaned).strip()


def _build_audio_url(audio: str) -> str:
    subdir = ""
    if audio.startswith("bix"):
        subdir = "bix"
    elif audio.startswith("gg"):
        subdir = "gg"
    elif audio[0].isdigit() or audio[0] in ("_", "'", ".", ","):
        subdir = "number"
    else:
        subdir = audio[0]
    return (
        f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{audio}.mp3"
    )


def _select_first_entry(payload: Any) -> dict | None:
    if not isinstance(payload, list):
        return None
    for item in payload:
        if isinstance(item, dict) and item.get("meta"):
            return item
    return None


def _extract_phonetics(entry: dict) -> list[dict[str, str | None]]:
    phonetics: list[dict[str, str | None]] = []
    hwi = entry.get("hwi") or {}
    for prs in hwi.get("prs") or []:
        if not isinstance(prs, dict):
            continue
        notation = prs.get("mw")
        audio_code = (
            prs.get("sound") or {}
        ).get("audio")
        audio_url = _build_audio_url(audio_code) if audio_code else None
        if notation or audio_url:
            phonetics.append(
                {
                    "notation": notation,
                    "audio_url": audio_url,
                }
            )
    return phonetics


def _extract_list_items(items: Any, key: str) -> list[str]:
    results: list[str] = []
    if not isinstance(items, list):
        return results
    for item in items:
        if not isinstance(item, dict):
            continue
        value = item.get(key)
        if isinstance(value, str) and value:
            results.append(value)
    return results


def _extract_variants(entry: dict) -> list[str]:
    variants: list[str] = []
    for variant in entry.get("vrs") or []:
        if not isinstance(variant, dict):
            continue
        base = variant.get("va")
        label = variant.get("vl")
        if not base:
            continue
        variants.append(f"{base} ({label})" if label else base)
    return variants


def _extract_inflections(entry: dict) -> list[str]:
    inflections: list[str] = []
    for item in entry.get("ins") or []:
        if not isinstance(item, dict):
            continue
        value = item.get("if")
        if not value:
            continue
        additions = item.get("ifc")
        if isinstance(additions, list):
            addition_text = ", ".join(
                addition for addition in additions if isinstance(addition, str)
            )
            if addition_text:
                value = f"{value} ({addition_text})"
        elif isinstance(additions, str) and additions:
            value = f"{value} ({additions})"
        inflections.append(value)
    return inflections


def _extract_definitions(entry: dict) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    definitions: list[dict[str, Any]] = []
    general_labels: set[str] = set()
    usage_labels: set[str] = set()
    parenthetical_labels: set[str] = set()
    def_blocks = entry.get("def") or []

    for block in def_blocks:
        sseq_list = block.get("sseq") or []
        for sense_seq in sseq_list:
            for sense_item in sense_seq:
                if not isinstance(sense_item, list) or len(sense_item) < 2:
                    continue
                sense_data = sense_item[1]
                if not isinstance(sense_data, dict):
                    continue
                dt_entries = sense_data.get("dt") or []
                meaning_parts: list[str] = []
                examples: list[str] = []
                for dt in dt_entries:
                    if not isinstance(dt, list) or len(dt) < 2:
                        continue
                    dt_type, dt_value = dt[0], dt[1]
                    if dt_type == "text" and isinstance(dt_value, str):
                        cleaned = _clean_text(dt_value)
                        if cleaned:
                            meaning_parts.append(cleaned)
                    elif dt_type == "vis" and isinstance(dt_value, list):
                        for vis in dt_value:
                            if isinstance(vis, dict):
                                example = _clean_text(vis.get("t"))
                                if example:
                                    examples.append(example)
                    elif dt_type == "uns" and isinstance(dt_value, list):
                        for uns in dt_value:
                            if (
                                isinstance(uns, list)
                                and len(uns) >= 2
                                and uns[0] == "text"
                                and isinstance(uns[1], str)
                            ):
                                cleaned = _clean_text(uns[1])
                                if cleaned:
                                    meaning_parts.append(cleaned)
                meaning = " ".join(part for part in meaning_parts if part).strip()
                if meaning:
                    definitions.append(
                        {
                            "meaning": meaning,
                            "examples": examples[:5],
                        }
                    )
                for label in sense_data.get("lbs") or []:
                    if isinstance(label, str):
                        general_labels.add(label)
                for label in sense_data.get("sls") or []:
                    if isinstance(label, str):
                        usage_labels.add(label)
                for label in sense_data.get("psl") or []:
                    if isinstance(label, str):
                        parenthetical_labels.add(label)

    if not definitions:
        for meaning in entry.get("shortdef") or []:
            cleaned = _clean_text(meaning)
            if cleaned:
                definitions.append({"meaning": cleaned, "examples": []})

    labels = {
        "general": sorted(general_labels),
        "usage": sorted(usage_labels),
        "parenthetical": sorted(parenthetical_labels),
    }
    return definitions[:10], labels


def _extract_etymology(entry: dict) -> str | None:
    et_data = entry.get("et") or []
    parts: list[str] = []
    for item in et_data:
        if not isinstance(item, list) or len(item) < 2:
            continue
        content = item[1]
        if isinstance(content, str):
            cleaned = _clean_text(content)
            if cleaned:
                parts.append(cleaned)
    return " ".join(parts).strip() or None


def _deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _extract_thesaurus_lists(entry: dict | None) -> tuple[list[str], list[str]]:
    if not isinstance(entry, dict):
        return [], []
    synonyms: list[str] = []
    antonyms: list[str] = []
    meta = entry.get("meta") or {}
    for group in meta.get("syns") or []:
        if isinstance(group, list):
            synonyms.extend(item for item in group if isinstance(item, str))
    for group in meta.get("ants") or []:
        if isinstance(group, list):
            antonyms.extend(item for item in group if isinstance(item, str))

    def_blocks = entry.get("def") or []
    for block in def_blocks:
        for sense_seq in block.get("sseq") or []:
            for sense_item in sense_seq:
                if not isinstance(sense_item, list) or len(sense_item) < 2:
                    continue
                sense_data = sense_item[1]
                if not isinstance(sense_data, dict):
                    continue
                for group in sense_data.get("syn_list") or []:
                    if isinstance(group, list):
                        for item in group:
                            if isinstance(item, dict):
                                word = item.get("wd")
                                if isinstance(word, str):
                                    synonyms.append(word)
                for group in sense_data.get("sim_list") or []:
                    if isinstance(group, list):
                        for item in group:
                            if isinstance(item, dict):
                                word = item.get("wd")
                                if isinstance(word, str):
                                    synonyms.append(word)
                for group in sense_data.get("ant_list") or []:
                    if isinstance(group, list):
                        for item in group:
                            if isinstance(item, dict):
                                word = item.get("wd")
                                if isinstance(word, str):
                                    antonyms.append(word)
    return _deduplicate(synonyms), _deduplicate(antonyms)


async def _fetch_dictionary_payload(
    client: httpx.AsyncClient, word: str
) -> dict:
    if not settings.merriam_dictionary_api_key:
        raise DictionaryLookupError("未配置 Merriam-Webster Dictionary API Key")
    url = f"{DICTIONARY_ENDPOINT}{word}"
    response = await client.get(
        url,
        params={"key": settings.merriam_dictionary_api_key},
    )
    response.raise_for_status()
    payload = response.json()
    entry = _select_first_entry(payload)
    if not entry:
        raise DictionaryEntryNotFound(f"未找到 {word} 的词典记录")
    return entry


async def _fetch_thesaurus_payload(
    client: httpx.AsyncClient, word: str
) -> dict | None:
    if not settings.merriam_thesaurus_api_key:
        return None
    url = f"{THESAURUS_ENDPOINT}{word}"
    response = await client.get(
        url,
        params={"key": settings.merriam_thesaurus_api_key},
    )
    response.raise_for_status()
    payload = response.json()
    return _select_first_entry(payload)


def _serialize_definitions(entry: DictionaryEntry) -> list[DefinitionSchema]:
    translation_map = {
        item.definition_index: item.translation
        for item in entry.translations or []
    }
    serialized: list[DefinitionSchema] = []
    raw_definitions = entry.definitions or []
    for index, raw_item in enumerate(raw_definitions):
        meaning = ""
        examples: list[str] = []
        if isinstance(raw_item, dict):
            meaning = str(raw_item.get("meaning") or "").strip()
            if isinstance(raw_item.get("examples"), list):
                examples = [
                    str(example)
                    for example in raw_item.get("examples")
                    if isinstance(example, str)
                ]
        elif isinstance(raw_item, str):
            meaning = raw_item.strip()
        if not meaning:
            continue
        serialized.append(
            DefinitionSchema(
                meaning=meaning,
                examples=examples,
                translation=translation_map.get(index),
            )
        )
    return serialized


def build_entry_response(entry: DictionaryEntry) -> DictionaryEntryResponse:
    return DictionaryEntryResponse(
        id=entry.id,
        word=entry.word,
        normalized_word=entry.normalized_word,
        part_of_speech=entry.part_of_speech,
        phonetics=entry.phonetics or [],
        variants=entry.variants or [],
        inflections=entry.inflections or [],
        definitions=_serialize_definitions(entry),
        synonyms=entry.synonyms or [],
        antonyms=entry.antonyms or [],
        labels=entry.labels or {},
        etymology=entry.etymology,
        chinese_translation=entry.chinese_translation,
        source=entry.source,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


async def get_or_fetch_entry(
    session: AsyncSession,
    word: str,
) -> DictionaryEntry:
    original_word, normalized_word = _normalize_word(word)
    cached = await dictionary_repo.get_by_normalized_word(
        session, normalized_word
    )
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(
            timeout=settings.dictionary_api_timeout_seconds
        ) as client:
            dictionary_payload = await _fetch_dictionary_payload(
                client, normalized_word
            )
            thesaurus_payload = await _fetch_thesaurus_payload(
                client, normalized_word
            )
    except DictionaryEntryNotFound:
        raise
    except httpx.HTTPStatusError as exc:
        logger.exception("词典 API 请求失败: %s", exc)
        raise DictionaryLookupError("查询词典接口失败，请稍后重试") from exc
    except httpx.HTTPError as exc:
        logger.exception("词典 API 网络错误: %s", exc)
        raise DictionaryLookupError("词典接口暂时不可用") from exc

    phonetics = _extract_phonetics(dictionary_payload)
    variants = _extract_variants(dictionary_payload)
    inflections = _extract_inflections(dictionary_payload)
    definitions, labels = _extract_definitions(dictionary_payload)
    etymology = _extract_etymology(dictionary_payload)
    synonyms, antonyms = _extract_thesaurus_lists(thesaurus_payload)

    display_word = dictionary_payload.get("hwi", {}).get("hw")
    if display_word:
        display_word = display_word.replace("*", "·")
    else:
        meta_id = dictionary_payload.get("meta", {}).get("id")
        display_word = meta_id.split(":")[0] if isinstance(meta_id, str) else original_word

    record = await dictionary_repo.create_entry(
        session,
        word=display_word or original_word,
        normalized_word=normalized_word,
        part_of_speech=dictionary_payload.get("fl"),
        phonetics=phonetics,
        variants=variants,
        inflections=inflections,
        definitions=definitions,
        synonyms=synonyms,
        antonyms=antonyms,
        labels=labels,
        etymology=etymology,
        chinese_translation=None,
        source="merriam-webster",
        source_metadata={
            "dictionary_entry": dictionary_payload.get("meta", {}).get("id"),
            "thesaurus_entry": (
                thesaurus_payload.get("meta", {}).get("id")
                if isinstance(thesaurus_payload, dict)
                else None
            ),
        },
    )
    record.translations = []
    return record
