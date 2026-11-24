#!/usr/bin/env python3
"""data/lessons.json からデザインアンテナの静的サイトを生成する。

使い方:
    python3 scripts/build.py

Python 標準ライブラリだけで動く。HTML はすべて検証が通ってから書く。
"""

from __future__ import annotations

import argparse
import html
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parent.parent

LESSON_KEYS = (
    "number",
    "date",
    "title",
    "titleEn",
    "category",
    "summary",
    "what",
    "example",
    "tip",
    "sources",
    "image",
    "imageAlt",
    "imageCaption",
)
SOURCE_KEYS = ("title", "url", "author", "year", "note")
TOP_KEYS = (
    "schemaVersion",
    "url",
    "title",
    "titleEn",
    "tagline",
    "description",
    "launch",
    "topics",
    "lessons",
)
LAUNCH_KEYS = ("date", "time", "timeLabel", "timezone")
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
SUMMARY_LIMIT = 56

MARK = """<svg class="mark" width="32" height="32" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
  <g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">
    <path d="M16 22.4V13"/>
    <path d="M10.1 15.1a7.4 7.4 0 0 1 11.8 0"/>
    <path d="M6.3 11.2a12.4 12.4 0 0 1 19.4 0"/>
  </g>
  <circle cx="16" cy="24.5" r="1.9" fill="currentColor"/>
</svg>"""

TOKEN = re.compile(r"(\[[^\]\n]+\]\(https?://[^\s)]+\)|\*\*[^*\n]+\*\*)")
LINK = re.compile(r"^\[([^\]\n]+)\]\((https?://[^\s)]+)\)$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CLOCK = re.compile(r"^\d{2}:\d{2}$")
ZONE = re.compile(r"^[+-]\d{2}:\d{2}$")

FOOTER_NOTES = (
    "文章は出典をもとに学習用に要約したものです。詳しくは各回の出典へ。",
    "図版には、AIで生成した画像が含まれることがあります。",
)


class BuildFailure(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="data/lessons.json から静的サイトを生成する")
    parser.add_argument("--root", type=Path, default=REPO, help="data/ と images/ があるディレクトリ")
    parser.add_argument("--out", type=Path, default=None, help="HTML の出力先。省略時は --root")
    return parser.parse_args(argv)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"キーが重複しています: {key}")
        seen[key] = value
    return seen


def load_json(path: Path) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise BuildFailure([f"{path} がありません。"]) from exc
    try:
        return json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise BuildFailure([f"{path} のJSONが正しくありません: {exc}"]) from exc
    except ValueError as exc:
        raise BuildFailure([f"{path}: {exc}"]) from exc


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def has_bad_controls(value: str, *, multiline: bool) -> bool:
    for char in value:
        code = ord(char)
        if code >= 32 or char == "\n" or (multiline and char == "\t"):
            if char == "\n" and not multiline:
                return True
            continue
        return True
    return False


def clean_string(
    value: Any,
    where: str,
    errors: list[str],
    *,
    multiline: bool = False,
) -> str | None:
    if not isinstance(value, str):
        errors.append(f"{where}: 文字列で書いてください。")
        return None
    text = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        errors.append(f"{where}: 空です。")
        return None
    if has_bad_controls(text, multiline=multiline):
        errors.append(f"{where}: 使えない制御文字があります。")
        return None
    return text


def optional_string(
    obj: dict[str, Any],
    key: str,
    where: str,
    errors: list[str],
    *,
    multiline: bool = False,
) -> str | None:
    if key not in obj:
        return None
    return clean_string(obj[key], f"{where}.{key}", errors, multiline=multiline)


def require_string(
    obj: dict[str, Any],
    key: str,
    where: str,
    errors: list[str],
    *,
    multiline: bool = False,
) -> str | None:
    if key not in obj:
        errors.append(f"{where}: {key} がありません。")
        return None
    return clean_string(obj[key], f"{where}.{key}", errors, multiline=multiline)


def unknown_keys(obj: dict[str, Any], allowed: tuple[str, ...], where: str, errors: list[str]) -> None:
    extra = [key for key in obj if key not in allowed]
    if extra:
        names = "、".join(extra)
        usable = "、".join(allowed)
        errors.append(f"{where}: 不明なキー（{names}）です。使えるキー: {usable}")


def parse_date(value: str, where: str, errors: list[str]) -> str | None:
    if not DATE.match(value):
        errors.append(f"{where}: YYYY-MM-DD で書いてください。")
        return None
    year, month, day = (int(part) for part in value.split("-"))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        errors.append(f"{where}: 実在する日付にしてください。")
        return None
    # Reject impossible days without pulling in calendar edge cases beyond 31.
    if month in {4, 6, 9, 11} and day > 30:
        errors.append(f"{where}: 実在する日付にしてください。")
        return None
    if month == 2:
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        if day > (29 if leap else 28):
            errors.append(f"{where}: 実在する日付にしてください。")
            return None
    return value


def date_ja(iso: str) -> str:
    year, month, day = (int(part) for part in iso.split("-"))
    return f"{year}年{month}月{day}日"


def date_dot(iso: str) -> str:
    year, month, day = iso.split("-")
    return f"{year}.{month}.{day}"


def check_http_url(value: str, where: str, errors: list[str]) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        errors.append(f"{where}: http または https のURLにしてください。")
        return None
    return value


def image_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    suffix = path.suffix.lower()
    size: tuple[int, int] | None = None
    if suffix == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        size = int(width), int(height)
    elif suffix == ".gif" and data.startswith((b"GIF87a", b"GIF89a")) and len(data) >= 10:
        width, height = struct.unpack("<HH", data[6:10])
        size = int(width), int(height)
    elif suffix in {".jpg", ".jpeg"}:
        size = jpeg_size(data)
    elif suffix == ".webp":
        size = webp_size(data)
    if size is None:
        return None
    width, height = size
    if width <= 0 or height <= 0 or width > 16000 or height > 16000:
        return None
    return width, height


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    index = 2
    while index + 1 < len(data):
        if data[index] != 0xFF:
            return None
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            return None
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
            continue
        if index + 2 > len(data):
            return None
        segment = int.from_bytes(data[index : index + 2], "big")
        if segment < 2 or index + segment > len(data):
            return None
        if marker in sof and segment >= 7:
            height, width = struct.unpack(">HH", data[index + 3 : index + 7])
            return int(width), int(height)
        if marker == 0xDA:
            return None
        index += segment
    return None


def webp_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if chunk == b"VP8 " and len(data) >= 30:
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L" and len(data) >= 25:
        b0, b1, b2, b3 = data[21:25]
        width = 1 + (((b1 & 0x3F) << 8) | b0)
        height = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
        return width, height
    return None


def lesson_filename(number: int) -> str:
    return f"{number:03d}.html"


def check_image(value: str, where: str, root: Path, errors: list[str]) -> tuple[str, tuple[int, int] | None] | None:
    if "\\" in value or value.startswith("/") or "://" in value:
        errors.append(f"{where}: images/ から始まる相対パスで書いてください。")
        return None
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] != "images":
        errors.append(f"{where}: images/ から始まる相対パスで書いてください。")
        return None
    if rel.suffix.lower() not in IMAGE_EXT:
        allowed = "、".join(sorted(IMAGE_EXT))
        errors.append(f"{where}: 拡張子は {allowed} のいずれかにしてください。")
        return None
    full = root / rel
    if not full.is_file():
        errors.append(f"{where}: ファイルがありません（{value}）。")
        return None
    return value.replace("\\", "/"), image_size(full)


def validate_source(source: Any, where: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(source, dict):
        errors.append(f"{where}: オブジェクトで書いてください。")
        return None
    unknown_keys(source, SOURCE_KEYS, where, errors)
    title = require_string(source, "title", where, errors)
    url = optional_string(source, "url", where, errors)
    if url is not None:
        url = check_http_url(url, f"{where}.url", errors)
    author = optional_string(source, "author", where, errors)
    note = optional_string(source, "note", where, errors, multiline=True)
    year: str | None = None
    if "year" in source:
        raw_year = source["year"]
        if is_int(raw_year):
            year = str(raw_year)
        elif isinstance(raw_year, str):
            year = clean_string(raw_year, f"{where}.year", errors)
        else:
            errors.append(f"{where}.year: 文字列か整数で書いてください。")
    if title is None:
        return None
    return {"title": title, "url": url, "author": author, "year": year, "note": note}


def strip_markdown(text: str) -> str:
    without_links = re.sub(r"\[([^\]\n]+)\]\(https?://[^\s)]+\)", r"\1", text)
    flat = without_links.replace("**", "")
    return re.sub(r"\s+", " ", flat).strip()


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def validate_lesson(
    lesson: Any,
    index: int,
    root: Path,
    errors: list[str],
    seen_numbers: set[int],
) -> dict[str, Any] | None:
    where = f"lessons[{index}]"
    if not isinstance(lesson, dict):
        errors.append(f"{where}: オブジェクトで書いてください。")
        return None
    unknown_keys(lesson, LESSON_KEYS, where, errors)
    number = lesson.get("number")
    if not is_int(number) or not 1 <= number <= 99999:
        errors.append(f"{where}.number: 1以上の整数にしてください。")
        number_ok = None
    else:
        number_ok = int(number)
        if number_ok in seen_numbers:
            errors.append(f"{where}.number: {number_ok} が重複しています。")
        seen_numbers.add(number_ok)
    date = require_string(lesson, "date", where, errors)
    if date is not None:
        date = parse_date(date, f"{where}.date", errors)
    title = require_string(lesson, "title", where, errors)
    title_en = optional_string(lesson, "titleEn", where, errors)
    category = require_string(lesson, "category", where, errors)
    summary = optional_string(lesson, "summary", where, errors)
    what = require_string(lesson, "what", where, errors, multiline=True)
    example = require_string(lesson, "example", where, errors, multiline=True)
    tip = require_string(lesson, "tip", where, errors, multiline=True)
    image_value = optional_string(lesson, "image", where, errors)
    image_alt = optional_string(lesson, "imageAlt", where, errors)
    image_caption = optional_string(lesson, "imageCaption", where, errors)
    image_info = None
    if image_value is not None:
        image_info = check_image(image_value, f"{where}.image", root, errors)
        if image_alt is None and "imageAlt" not in lesson:
            errors.append(f"{where}: 画像があるときは imageAlt も書いてください。")
    elif "imageAlt" in lesson or "imageCaption" in lesson:
        errors.append(f"{where}: imageAlt と imageCaption は image と一緒に書いてください。")
    sources_raw = lesson.get("sources", None)
    sources: list[dict[str, Any]] = []
    if not isinstance(sources_raw, list) or not sources_raw:
        errors.append(f"{where}.sources: 出典を1件以上書いてください。")
    else:
        for source_index, source in enumerate(sources_raw):
            cleaned = validate_source(source, f"{where}.sources[{source_index}]", errors)
            if cleaned is not None:
                sources.append(cleaned)
    if None in {date, title, category, what, example, tip} or number_ok is None:
        return None
    if not sources:
        return None
    assert date and title and category and what and example and tip
    summary_source = summary if summary is not None else strip_markdown(what)
    return {
        "number": number_ok,
        "date": date,
        "date_ja": date_ja(date),
        "date_dot": date_dot(date),
        "title": title,
        "title_en": title_en,
        "category": category,
        "summary": truncate(strip_markdown(summary_source), SUMMARY_LIMIT),
        "what": what,
        "example": example,
        "tip": tip,
        "sources": sources,
        "image": None if image_info is None else image_info[0],
        "image_alt": image_alt,
        "image_caption": image_caption,
        "image_size": None if image_info is None else image_info[1],
        "filename": lesson_filename(number_ok),
    }


def validate(data: Any, root: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        raise BuildFailure(["data/lessons.json の最上位はオブジェクトにしてください。"])
    unknown_keys(data, TOP_KEYS, "lessons.json", errors)
    version = data.get("schemaVersion")
    if version != 1:
        errors.append("schemaVersion: 1 にしてください。")
    url = require_string(data, "url", "lessons.json", errors)
    if url is not None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append("url: https の公開URLにしてください。")
        url = url.rstrip("/")
    title = require_string(data, "title", "lessons.json", errors)
    title_en = require_string(data, "titleEn", "lessons.json", errors)
    tagline = require_string(data, "tagline", "lessons.json", errors)
    description = require_string(data, "description", "lessons.json", errors)
    launch_raw = data.get("launch")
    launch = None
    if not isinstance(launch_raw, dict):
        errors.append("launch: オブジェクトで書いてください。")
    else:
        unknown_keys(launch_raw, LAUNCH_KEYS, "launch", errors)
        launch_date = require_string(launch_raw, "date", "launch", errors)
        if launch_date is not None:
            launch_date = parse_date(launch_date, "launch.date", errors)
        launch_time = require_string(launch_raw, "time", "launch", errors)
        if launch_time is not None and not CLOCK.match(launch_time):
            errors.append("launch.time: HH:MM で書いてください。")
            launch_time = None
        time_label = require_string(launch_raw, "timeLabel", "launch", errors)
        timezone = require_string(launch_raw, "timezone", "launch", errors)
        if timezone is not None and not ZONE.match(timezone):
            errors.append("launch.timezone: +09:00 の形で書いてください。")
            timezone = None
        if None not in {launch_date, launch_time, time_label, timezone}:
            assert launch_date and launch_time and time_label and timezone
            launch = {
                "date": launch_date,
                "date_ja": date_ja(launch_date),
                "time": launch_time,
                "time_label": time_label,
                "timezone": timezone,
                "datetime": f"{launch_date}T{launch_time}:00{timezone}",
            }
    topics_raw = data.get("topics")
    topics: list[str] = []
    if not isinstance(topics_raw, list):
        errors.append("topics: 文字列の配列にしてください。")
    else:
        for index, topic in enumerate(topics_raw):
            cleaned = clean_string(topic, f"topics[{index}]", errors)
            if cleaned is not None:
                topics.append(cleaned)
    lessons_raw = data.get("lessons")
    lessons: list[dict[str, Any]] = []
    seen_numbers: set[int] = set()
    if not isinstance(lessons_raw, list):
        errors.append("lessons: 配列にしてください。空でもかまいません。")
    else:
        for index, lesson in enumerate(lessons_raw):
            cleaned = validate_lesson(lesson, index, root, errors, seen_numbers)
            if cleaned is not None:
                lessons.append(cleaned)
    if errors:
        raise BuildFailure(errors)
    assert url and title and title_en and tagline and description and launch
    return {
        "url": url,
        "title": title,
        "title_en": title_en,
        "tagline": tagline,
        "description": description,
        "launch": launch,
        "topics": topics,
        "lessons": lessons,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_inline(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        parts: list[str] = []
        position = 0
        for match in TOKEN.finditer(line):
            parts.append(esc(line[position : match.start()]))
            token = match.group(0)
            link = LINK.match(token)
            if link:
                parts.append(f'<a href="{esc(link.group(2))}">{esc(link.group(1))}</a>')
            else:
                parts.append(f"<strong>{esc(token[2:-2])}</strong>")
            position = match.end()
        parts.append(esc(line[position:]))
        lines.append("".join(parts))
    return "<br>\n".join(lines)


def render_prose(text: str) -> str:
    chunks = re.split(r"\n\s*\n", text.strip())
    paragraphs = []
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk:
            paragraphs.append(f"<p>{render_inline(chunk)}</p>")
    return "\n".join(paragraphs)


def render_sources(sources: list[dict[str, Any]]) -> str:
    items = []
    for source in sources:
        meta_bits = [bit for bit in (source["author"], source["year"]) if bit]
        bits = []
        if source["url"]:
            bits.append(f'<a class="source-title" href="{esc(source["url"])}">{esc(source["title"])}</a>')
        else:
            bits.append(f'<span class="source-title">{esc(source["title"])}</span>')
        if meta_bits:
            bits.append(f'<span class="source-meta">{esc(" · ".join(meta_bits))}</span>')
        if source["url"]:
            bits.append(f'<span class="source-url">{esc(source["url"])}</span>')
        if source["note"]:
            bits.append(f'<span class="source-note">{render_inline(source["note"])}</span>')
        items.append("          <li>\n            " + "\n            ".join(bits) + "\n          </li>")
    return "\n".join(items)


def footer(home_href: str, title: str) -> str:
    notes = "\n".join(f"        <li>{esc(note)}</li>" for note in FOOTER_NOTES)
    return f"""<footer class="site-footer">
      <div class="wrap">
        <p class="footer-name"><a href="{esc(home_href)}">{esc(title)}</a></p>
        <ul class="footer-notes">
{notes}
        </ul>
      </div>
    </footer>"""


def brand_link(home_href: str, title: str, title_en: str) -> str:
    return f"""<a class="brand" href="{esc(home_href)}">
        {MARK}
        <span class="brand-text">
          <span class="brand-en" lang="en">{esc(title_en)}</span>
          <span class="brand-ja">{esc(title)}</span>
        </span>
      </a>"""


def site_header(home_href: str, title: str, title_en: str) -> str:
    return f"""<header class="top">
    <div class="wrap top-inner">
      {brand_link(home_href, title, title_en)}
      <nav class="top-nav" aria-label="サイト">
        <a href="{esc(home_href)}">目次</a>
      </nav>
    </div>
  </header>"""


def document(
    *,
    body_class: str,
    title: str,
    description: str,
    canonical: str,
    asset_prefix: str,
    og_type: str,
    inner: str,
    inline_css: str | None = None,
    robots: str | None = None,
    extra_head: str = "",
    published: str | None = None,
    section: str | None = None,
    prev_href: str | None = None,
    next_href: str | None = None,
) -> str:
    description = re.sub(r"\s+", " ", description).strip()
    if inline_css is not None:
        if "</style" in inline_css.lower():
            raise BuildFailure(["css/style.css に </style が含まれているため、404ページに埋め込めません。"])
        style = f"<style>\n{inline_css}\n</style>"
    else:
        style = f'<link rel="stylesheet" href="{esc(asset_prefix)}css/style.css">'
    robots_tag = f'\n  <meta name="robots" content="{esc(robots)}">' if robots else ""
    published_tag = (
        f'\n  <meta property="article:published_time" content="{esc(published)}">' if published else ""
    )
    section_tag = f'\n  <meta property="article:section" content="{esc(section)}">' if section else ""
    prev_tag = f'\n  <link rel="prev" href="{esc(prev_href)}">' if prev_href else ""
    next_tag = f'\n  <link rel="next" href="{esc(next_href)}">' if next_href else ""
    extra = f"\n  {extra_head}" if extra_head else ""
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- data/lessons.json から scripts/build.py が生成。手で編集しない。 -->
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="theme-color" content="#0d3b66">
  <meta property="og:locale" content="ja_JP">
  <meta property="og:site_name" content="デザインアンテナ">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:type" content="{esc(og_type)}">{published_tag}{section_tag}
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="{esc(asset_prefix)}favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=IBM+Plex+Sans+JP:wght@400;500;600&amp;family=Newsreader:ital,wght@0,400;0,500;0,600;1,400;1,500&amp;display=swap">{robots_tag}{prev_tag}{next_tag}
  {style}{extra}
</head>
<body class="{esc(body_class)}">
  <a class="skip" href="#main">本文へ</a>
  <div class="topline" aria-hidden="true"></div>
  {inner}
</body>
</html>
"""


def ordered_categories(lessons: list[dict[str, Any]], topics: list[str]) -> list[str]:
    present: list[str] = []
    seen: set[str] = set()
    for topic in topics:
        if any(lesson["category"] == topic for lesson in lessons) and topic not in seen:
            present.append(topic)
            seen.add(topic)
    for lesson in sorted(lessons, key=lambda item: item["number"]):
        if lesson["category"] not in seen:
            present.append(lesson["category"])
            seen.add(lesson["category"])
    return present


def render_filters(categories: list[tuple[str, str, int]], total: int) -> tuple[str, str]:
    choices = [
        f"""<label class="choice">
          <input type="radio" name="category" id="filter-all" checked>
          <span class="choice-label">すべて</span>
          <span class="choice-n">{total}</span>
        </label>"""
    ]
    css_rules = []
    for input_id, label, count in categories:
        value = input_id.removeprefix("filter-")
        choices.append(
            f"""<label class="choice">
          <input type="radio" name="category" id="{esc(input_id)}">
          <span class="choice-label">{esc(label)}</span>
          <span class="choice-n">{count}</span>
        </label>"""
        )
        css_rules.append(
            f'body:has(#{input_id}:checked) .toc-item:not([data-filter="{value}"]){{display:none}}'
        )
    html_block = f"""<fieldset class="filters">
        <legend>カテゴリで絞り込む</legend>
        <div class="choices">
          {"".join(choices)}
        </div>
      </fieldset>"""
    style = "<style>\n" + "\n".join(css_rules) + "\n</style>"
    return html_block, style


def render_toc_item(lesson: dict[str, Any], filter_id: str) -> str:
    thumb = ""
    link_class = "toc-link"
    if lesson["image"]:
        link_class += " has-thumb"
        size = ""
        if lesson["image_size"]:
            width, height = lesson["image_size"]
            size = f' width="{width}" height="{height}"'
        thumb = (
            f'\n        <img class="toc-thumb" src="{esc(lesson["image"])}" alt=""{size}'
            ' loading="lazy" decoding="async">'
        )
    english = ""
    if lesson["title_en"]:
        english = f'\n        <p class="toc-en" lang="en">{esc(lesson["title_en"])}</p>'
    return f"""<li class="toc-item" role="listitem" data-filter="{esc(filter_id)}">
      <a class="{link_class}" href="lessons/{esc(lesson["filename"])}">
        <p class="toc-meta"><span class="toc-no">第{lesson["number"]}回</span><time class="dot-date" datetime="{esc(lesson["date"])}">{esc(lesson["date_dot"])}</time></p>
        <p class="toc-cat">{esc(lesson["category"])}</p>
        <h2 class="toc-title">{esc(lesson["title"])}</h2>{english}
        <p class="toc-summary">{esc(lesson["summary"])}</p>{thumb}
      </a>
    </li>"""


def render_index(site: dict[str, Any]) -> str:
    launch = site["launch"]
    lessons = sorted(site["lessons"], key=lambda item: (item["date"], item["number"]), reverse=True)
    if lessons:
        categories = ordered_categories(site["lessons"], site["topics"])
        counts: dict[str, int] = {}
        for lesson in site["lessons"]:
            counts[lesson["category"]] = counts.get(lesson["category"], 0) + 1
        filter_ids = {category: f"c{index}" for index, category in enumerate(categories, start=1)}
        filter_html, filter_css = render_filters(
            [(f"filter-{filter_ids[category]}", category, counts[category]) for category in categories],
            len(lessons),
        )
        latest = lessons[0]
        listing = f"""<p class="count">全<span class="num">{len(lessons)}</span>回、最新は<time datetime="{esc(latest["date"])}">{esc(latest["date_ja"])}</time></p>
      {filter_html}
      <ol class="toc" role="list" aria-label="レッスン">
        {"".join(render_toc_item(lesson, filter_ids[lesson["category"]]) for lesson in lessons)}
      </ol>"""
        extra_head = filter_css
    else:
        topics = "\n".join(f'          <li role="listitem">{esc(topic)}</li>' for topic in site["topics"])
        topic_block = ""
        if topics:
            topic_block = f"""
      <section class="themes" aria-labelledby="themes-title">
        <h2 id="themes-title">これから扱うテーマ</h2>
        <ul class="topics" role="list">
{topics}
        </ul>
      </section>"""
        listing = f"""<section class="empty" aria-labelledby="empty-title">
        <p class="empty-no" lang="en">No. 001</p>
        <h2 id="empty-title"><span class="empty-line">最初のレッスンは、</span><span class="empty-when"><time datetime="{esc(launch["datetime"])}"><span class="empty-keep">{esc(launch["date_ja"])}</span> <span class="empty-keep">{esc(launch["time_label"])}に届きます。</span></time></span></h2>
        <p class="empty-note">第1回から、この目次に新しい順で並びます。</p>
      </section>{topic_block}"""
        extra_head = ""
    inner = f"""<header class="masthead">
    <div class="wrap">
      <h1 class="site-title">
        <span class="kicker" lang="en">{MARK}<span>{esc(site["title_en"])}</span></span>
        <span class="site-ja">{esc(site["title"])}</span>
      </h1>
      <p class="tagline">{esc(site["tagline"])}</p>
      <p class="lede">{esc(site["description"])}</p>
      <p class="schedule">新しい回は、毎日 {esc(launch["time_label"])}（日本時間）に追加します。</p>
    </div>
  </header>
  <main id="main" tabindex="-1">
    <div class="wrap">
      {listing}
    </div>
  </main>
  {footer("index.html", site["title"])}"""
    return document(
        body_class="page-index",
        title=f'{site["title"]}｜{site["tagline"]}',
        description=site["description"],
        canonical=site["url"] + "/",
        asset_prefix="",
        og_type="website",
        inner=inner,
        extra_head=extra_head,
    )


def render_pager(prev_lesson: dict[str, Any] | None, next_lesson: dict[str, Any] | None) -> str:
    def slot(kind: str, lesson: dict[str, Any] | None, empty_label: str) -> str:
        css = "pager-slot pager-next" if kind == "next" else "pager-slot"
        label = "次の回" if kind == "next" else "前の回"
        if lesson is None:
            body = f"""<p class="pager-none">
          <span class="pager-label">{label}</span>
          <span class="pager-title">{empty_label}</span>
        </p>"""
        else:
            body = f"""<a class="pager-link" href="{esc(lesson["filename"])}">
          <span class="pager-label">{label}</span>
          <span class="pager-title">第{lesson["number"]}回 {esc(lesson["title"])}</span>
        </a>"""
        return f'<div class="{css}">\n        {body}\n      </div>'

    return f"""<nav class="pager" aria-label="前後の回">
      {slot("prev", prev_lesson, "これが最初の回です")}
      {slot("next", next_lesson, "これが最新の回です")}
    </nav>"""


def render_lesson(
    site: dict[str, Any],
    lesson: dict[str, Any],
    prev_lesson: dict[str, Any] | None,
    next_lesson: dict[str, Any] | None,
) -> str:
    english = ""
    if lesson["title_en"]:
        english = f'\n        <p class="title-en" lang="en">{esc(lesson["title_en"])}</p>'
    figure = ""
    if lesson["image"]:
        size = ""
        if lesson["image_size"]:
            width, height = lesson["image_size"]
            size = f' width="{width}" height="{height}"'
        caption = ""
        if lesson["image_caption"]:
            caption = f'\n          <figcaption>{esc(lesson["image_caption"])}</figcaption>'
        figure = f"""
      <figure class="figure">
          <img src="../{esc(lesson["image"])}" alt="{esc(lesson["image_alt"])}"{size} decoding="async">{caption}
        </figure>"""
    home = "../index.html"
    inner = f"""{site_header(home, site["title"], site["title_en"])}
  <main id="main" tabindex="-1">
    <article class="wrap lesson">
      <header class="lesson-head">
        <p class="issue"><span class="issue-affix">第</span><span class="issue-num">{lesson["number"]}</span><span class="issue-affix">回</span></p>
        <p class="lesson-meta"><time datetime="{esc(lesson["date"])}">{esc(lesson["date_ja"])}</time><span class="sep" aria-hidden="true">·</span><span class="lesson-cat">{esc(lesson["category"])}</span></p>
        <h1 class="lesson-title">{esc(lesson["title"])}</h1>{english}
      </header>{figure}
      <section class="block">
        <h2><span class="idx" aria-hidden="true">01</span>どういう知識か</h2>
        <div class="prose">
          {render_prose(lesson["what"])}
        </div>
      </section>
      <section class="block">
        <h2><span class="idx" aria-hidden="true">02</span>具体例</h2>
        <div class="prose">
          {render_prose(lesson["example"])}
        </div>
      </section>
      <section class="block tip">
        <h2><span class="idx" aria-hidden="true">03</span>今日から使えるひとこと</h2>
        <blockquote>
          {render_prose(lesson["tip"])}
        </blockquote>
      </section>
      <section class="sources" aria-labelledby="sources-title">
        <h2 id="sources-title">出典</h2>
        <ol>
{render_sources(lesson["sources"])}
        </ol>
      </section>
      {render_pager(prev_lesson, next_lesson)}
    </article>
  </main>
  {footer(home, site["title"])}"""
    description = lesson["summary"]
    return document(
        body_class="page-lesson",
        title=f'第{lesson["number"]}回 {lesson["title"]}｜{site["title"]}',
        description=description,
        canonical=lesson_url(site, lesson),
        asset_prefix="../",
        og_type="article",
        inner=inner,
        published=lesson["date"],
        section=lesson["category"],
        prev_href=None if prev_lesson is None else prev_lesson["filename"],
        next_href=None if next_lesson is None else next_lesson["filename"],
    )


def render_simple(
    site: dict[str, Any],
    *,
    page_title: str,
    heading: str,
    paragraphs: list[str],
    home_href: str,
    asset_prefix: str,
    canonical: str,
    issue: str | None = None,
    inline_css: str | None = None,
) -> str:
    issue_html = ""
    if issue:
        issue_html = f'<p class="issue"><span class="issue-num">{esc(issue)}</span></p>\n        '
    prose = "\n          ".join(f"<p>{paragraph}</p>" for paragraph in paragraphs)
    inner = f"""{site_header(home_href, site["title"], site["title_en"])}
  <main id="main" tabindex="-1">
    <article class="wrap lesson">
      <header class="lesson-head">
        {issue_html}<h1 class="lesson-title">{esc(heading)}</h1>
      </header>
      <div class="prose">
          {prose}
      </div>
    </article>
  </main>
  {footer(home_href, site["title"])}"""
    return document(
        body_class="page-simple",
        title=f"{page_title}｜{site['title']}",
        description=heading,
        canonical=canonical,
        asset_prefix=asset_prefix,
        og_type="website",
        inner=inner,
        inline_css=inline_css,
        robots="noindex",
    )


def lesson_url(site: dict[str, Any], lesson: dict[str, Any]) -> str:
    return f"{site['url']}/lessons/{lesson['filename'].removesuffix('.html')}"


def render_sitemap(site: dict[str, Any]) -> str:
    lessons = sorted(site["lessons"], key=lambda item: item["number"])
    lastmod = lessons[-1]["date"] if lessons else site["launch"]["date"]
    urls = [f"  <url>\n    <loc>{esc(site['url'] + '/')}</loc>\n    <lastmod>{esc(lastmod)}</lastmod>\n  </url>"]
    for lesson in lessons:
        loc = lesson_url(site, lesson)
        urls.append(
            f"  <url>\n    <loc>{esc(loc)}</loc>\n    <lastmod>{esc(lesson['date'])}</lastmod>\n  </url>"
        )
    body = "\n".join(urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def render_robots(site: dict[str, Any]) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {site['url']}/sitemap.xml\n"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def build(root: Path, out: Path) -> list[str]:
    css_path = root / "css" / "style.css"
    favicon = root / "favicon.svg"
    missing = [str(path.relative_to(root)) for path in (css_path, favicon) if not path.is_file()]
    if missing:
        raise BuildFailure([f"必要なファイルがありません: {'、'.join(missing)}"])
    site = validate(load_json(root / "data" / "lessons.json"), root)
    by_number = sorted(site["lessons"], key=lambda item: item["number"])
    pages: dict[Path, str] = {}
    pages[out / "index.html"] = render_index(site)
    pages[out / "sitemap.xml"] = render_sitemap(site)
    pages[out / "robots.txt"] = render_robots(site)
    inline_css = css_path.read_text(encoding="utf-8")
    base = site["url"] + "/"
    pages[out / "404.html"] = render_simple(
        site,
        page_title="ページが見つかりません",
        heading="ページが見つかりません",
        paragraphs=[
            "アドレスが変わったか、まだ公開されていない回です。",
            f'<a href="{esc(base)}">目次へ戻る</a>',
        ],
        home_href=base,
        asset_prefix=base,
        canonical=base,
        issue="404",
        inline_css=inline_css,
    )
    pages[out / "lessons" / "index.html"] = render_simple(
        site,
        page_title="レッスン",
        heading="レッスンは目次にまとまっています",
        paragraphs=[
            "各回のページは、サイトの目次から開きます。",
            '<a href="../index.html">目次へ戻る</a>',
        ],
        home_href="../index.html",
        asset_prefix="../",
        canonical=base,
    )
    expected = {"index.html"}
    for index, lesson in enumerate(by_number):
        prev_lesson = by_number[index - 1] if index > 0 else None
        next_lesson = by_number[index + 1] if index + 1 < len(by_number) else None
        name = lesson["filename"]
        expected.add(name)
        pages[out / "lessons" / name] = render_lesson(site, lesson, prev_lesson, next_lesson)
    for path, text in pages.items():
        write_text(path, text)
    removed: list[str] = []
    lessons_dir = out / "lessons"
    if lessons_dir.is_dir():
        for path in sorted(lessons_dir.glob("*.html")):
            if path.name not in expected:
                path.unlink()
                removed.append(path.name)
    return removed


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    out = args.out.resolve() if args.out else root
    try:
        removed = build(root, out)
    except BuildFailure as exc:
        for error in exc.errors:
            print(error, file=sys.stderr)
        return 1
    count = len(json.loads((root / "data" / "lessons.json").read_text(encoding="utf-8"))["lessons"])
    print(f"書き出しました。レッスン {count} 件。")
    if removed:
        print("古いページを削除しました: " + "、".join(removed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
