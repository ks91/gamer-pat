#!/usr/bin/env python3
"""Extract highlight annotations from a PDF and map them to highlighted text.

Uses only the standard library plus the external `pdftotext -bbox-layout`
command that is already available in this environment.
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass
from pathlib import Path


OBJ_RE = re.compile(rb"(\d+)\s+0\s+obj(.*?)endobj", re.S)
PAGE_RE = re.compile(rb"/Type(?:\s*|)/Page\b")
PAGES_RE = re.compile(rb"/Type(?:\s*|)/Pages\b")
CATALOG_PAGES_RE = re.compile(rb"/Pages\s+(\d+)\s+0\s+R")
KIDS_RE = re.compile(rb"/Kids\s*\[([^\]]+)\]", re.S)
REF_RE = re.compile(rb"(\d+)\s+0\s+R")
PARENT_RE = re.compile(r"/P\s+(\d+)\s+0\s+R")
QUAD_RE = re.compile(r"/QuadPoints\s*\[([^\]]+)\]", re.S)
RECT_RE = re.compile(r"/Rect\s*\[([^\]]+)\]", re.S)
SUBTYPE_RE = re.compile(r"/Subtype\s*/([A-Za-z]+)")
ASCII_WORD_RE = re.compile(r"[A-Za-z0-9]")
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
INVALID_XML_CHARS_RE = re.compile(
    "[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]"
)


@dataclass
class Word:
    text: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class Line:
    text: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class Annotation:
    obj_num: int
    page_ref: int
    page_num: int
    comment: str
    quads: list[tuple[float, float, float, float]]
    target: str
    context: str
    sort_y: float


def needs_space_between(left: str, right: str, gap: float) -> bool:
    if gap <= 0.5:
        return False
    if not left or not right:
        return False
    if CJK_RE.search(left) or CJK_RE.search(right):
        return False
    if left.endswith(("-", "/", "(")) or right.startswith(("-", "/", ")", ".", ",", ";", ":", "!", "?")):
        return False
    return bool(ASCII_WORD_RE.search(left) and ASCII_WORD_RE.search(right))


def join_words_with_layout(words: list[Word]) -> str:
    if not words:
        return ""
    sorted_words = sorted(words, key=lambda w: (round(w.y_min, 1), w.x_min))
    parts = [sorted_words[0].text]
    prev = sorted_words[0]
    for word in sorted_words[1:]:
        gap = word.x_min - prev.x_max
        if needs_space_between(prev.text, word.text, gap):
            parts.append(" ")
        parts.append(word.text)
        prev = word
    return "".join(parts).strip()


def parse_pdf_literal(text: str, start_idx: int) -> tuple[str, int]:
    assert text[start_idx] == "("
    i = start_idx + 1
    depth = 1
    out: list[str] = []
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            if i + 1 >= len(text):
                break
            nxt = text[i + 1]
            if nxt in r"nrtbf()\\":
                mapping = {
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                    "b": "\b",
                    "f": "\f",
                    "(": "(",
                    ")": ")",
                    "\\": "\\",
                }
                out.append(mapping[nxt])
                i += 2
                continue
            if nxt in "\n\r":
                i += 2
                continue
            octal = text[i + 1 : i + 4]
            if re.fullmatch(r"[0-7]{1,3}", octal[: len(octal.rstrip())]):
                m = re.match(r"[0-7]{1,3}", text[i + 1 : i + 4])
                if m:
                    out.append(chr(int(m.group(0), 8)))
                    i += 1 + len(m.group(0))
                    continue
            out.append(nxt)
            i += 2
            continue
        if ch == "(":
            depth += 1
            out.append(ch)
            i += 1
            continue
        if ch == ")":
            depth -= 1
            if depth == 0:
                return "".join(out), i + 1
            out.append(ch)
            i += 1
            continue
        out.append(ch)
        i += 1
    raise ValueError("unterminated PDF literal string")


def extract_field(obj_text: str, key: str) -> str | None:
    marker = f"/{key}("
    idx = obj_text.find(marker)
    if idx == -1:
        return None
    value, _ = parse_pdf_literal(obj_text, idx + len(key) + 1)
    return value


def extract_stream_bytes(body: bytes) -> bytes | None:
    stream_pos = body.find(b"stream")
    if stream_pos == -1:
        return None
    start = stream_pos + len(b"stream")
    if body[start : start + 2] == b"\r\n":
        start += 2
    elif body[start : start + 1] in (b"\r", b"\n"):
        start += 1
    end = body.rfind(b"endstream")
    if end == -1 or end < start:
        return None
    return body[start:end]


def expand_object_stream(body: bytes) -> dict[int, bytes]:
    n_match = re.search(rb"/N\s+(\d+)", body)
    first_match = re.search(rb"/First\s+(\d+)", body)
    if not n_match or not first_match:
        return {}
    stream = extract_stream_bytes(body)
    if stream is None:
        return {}
    try:
        data = zlib.decompress(stream)
    except zlib.error:
        return {}
    first = int(first_match.group(1))
    header = data[:first].decode("latin1", errors="ignore").strip().split()
    pairs = []
    for i in range(0, len(header), 2):
        if i + 1 >= len(header):
            break
        try:
            pairs.append((int(header[i]), int(header[i + 1])))
        except ValueError:
            continue
    objects: dict[int, bytes] = {}
    body_bytes = data[first:]
    for idx, (obj_num, offset) in enumerate(pairs):
        next_offset = pairs[idx + 1][1] if idx + 1 < len(pairs) else len(body_bytes)
        objects[obj_num] = body_bytes[offset:next_offset]
    return objects


def load_all_objects(pdf_bytes: bytes) -> dict[int, bytes]:
    objects: dict[int, bytes] = {}
    direct = list(OBJ_RE.finditer(pdf_bytes))
    for match in direct:
        obj_num = int(match.group(1))
        body = match.group(2)
        objects[obj_num] = body
    for match in direct:
        body = match.group(2)
        if b"/Type/ObjStm" in body or b"/Type /ObjStm" in body:
            for obj_num, embedded in expand_object_stream(body).items():
                objects[obj_num] = embedded
    return objects


def collect_page_order(objects: dict[int, bytes]) -> list[int]:
    pages_root = None
    for body in objects.values():
        if b"/Type/Catalog" in body or b"/Type /Catalog" in body:
            match = CATALOG_PAGES_RE.search(body)
            if match:
                pages_root = int(match.group(1))
                break

    seen: set[int] = set()

    def walk(obj_num: int) -> list[int]:
        if obj_num in seen:
            return []
        seen.add(obj_num)
        body = objects.get(obj_num, b"")
        if PAGE_RE.search(body):
            return [obj_num]
        if not PAGES_RE.search(body):
            return []
        kids_match = KIDS_RE.search(body)
        if not kids_match:
            return []
        pages: list[int] = []
        for ref in REF_RE.finditer(kids_match.group(1)):
            pages.extend(walk(int(ref.group(1))))
        return pages

    if pages_root is not None:
        page_order = walk(pages_root)
        if page_order:
            return page_order

    return sorted(obj_num for obj_num, body in objects.items() if PAGE_RE.search(body))


def clean_comment(raw: str) -> str:
    text = raw
    try:
        repaired = raw.encode("latin1").decode("utf-8")
    except UnicodeError:
        repaired = None
    if repaired:
        text = repaired
    if raw.lstrip().startswith("<?xml"):
        text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\r", "\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()


def parse_bbox_xhtml(xhtml_bytes: bytes) -> ET.Element:
    sanitized = INVALID_XML_CHARS_RE.sub("", xhtml_bytes.decode("utf-8", errors="replace"))
    return ET.fromstring(sanitized)


def load_pages_from_bbox(pdf_path: Path) -> tuple[dict[int, list[Word]], dict[int, list[Line]], dict[int, float]]:
    with tempfile.NamedTemporaryFile(suffix=".xhtml") as tmp:
        subprocess.run(
            ["pdftotext", "-bbox-layout", str(pdf_path), tmp.name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        root = parse_bbox_xhtml(Path(tmp.name).read_bytes())
    pages_words: dict[int, list[Word]] = {}
    pages_lines: dict[int, list[Line]] = {}
    page_heights: dict[int, float] = {}

    def descendants(node: ET.Element, tag: str) -> list[ET.Element]:
        return [elem for elem in node.iter() if elem.tag.rsplit("}", 1)[-1] == tag]

    for page_idx, page in enumerate(descendants(root, "page"), start=1):
        page_heights[page_idx] = float(page.attrib["height"])
        words: list[Word] = []
        lines: list[Line] = []
        for line in descendants(page, "line"):
            line_words = []
            for word in descendants(line, "word"):
                text = "".join(word.itertext()).strip()
                if not text:
                    continue
                w = Word(
                    text=text,
                    x_min=float(word.attrib["xMin"]),
                    y_min=float(word.attrib["yMin"]),
                    x_max=float(word.attrib["xMax"]),
                    y_max=float(word.attrib["yMax"]),
                )
                words.append(w)
                line_words.append(w)
            if line_words:
                lines.append(
                    Line(
                        text=join_words_with_layout(line_words),
                        x_min=min(w.x_min for w in line_words),
                        y_min=min(w.y_min for w in line_words),
                        x_max=max(w.x_max for w in line_words),
                        y_max=max(w.y_max for w in line_words),
                    )
                )
        pages_words[page_idx] = words
        pages_lines[page_idx] = lines
    return pages_words, pages_lines, page_heights


def overlap(a0: float, a1: float, b0: float, b1: float) -> bool:
    return min(a1, b1) > max(a0, b0)


def words_in_rect(words: list[Word], rect: tuple[float, float, float, float]) -> list[Word]:
    x0, y0, x1, y1 = rect
    hits = []
    for word in words:
        if overlap(word.x_min, word.x_max, x0, x1) and overlap(word.y_min, word.y_max, y0, y1):
            hits.append(word)
    return hits


def lines_near_rect(lines: list[Line], rect: tuple[float, float, float, float]) -> list[Line]:
    x0, y0, x1, y1 = rect
    hits = []
    for line in lines:
        same_band = overlap(line.y_min, line.y_max, y0 - 6, y1 + 6)
        nearby_x = not (line.x_max < x0 - 80 or line.x_min > x1 + 80)
        if same_band and nearby_x:
            hits.append(line)
    return hits


def nearest_lines(lines: list[Line], rect: tuple[float, float, float, float], limit: int = 3) -> list[Line]:
    x0, y0, x1, y1 = rect
    rcx = (x0 + x1) / 2
    rcy = (y0 + y1) / 2
    ranked = []
    for line in lines:
        lcx = (line.x_min + line.x_max) / 2
        lcy = (line.y_min + line.y_max) / 2
        dist = ((lcx - rcx) ** 2 + (lcy - rcy) ** 2) ** 0.5
        ranked.append((dist, line.y_min, line.x_min, line))
    ranked.sort(key=lambda row: row[:3])
    return [row[3] for row in ranked[:limit]]


def normalize_quads(raw: str, page_height: float) -> list[tuple[float, float, float, float]]:
    nums = [float(x) for x in raw.split()]
    rects = []
    for i in range(0, len(nums), 8):
        chunk = nums[i : i + 8]
        if len(chunk) < 8:
            continue
        xs = [chunk[0], chunk[2], chunk[4], chunk[6]]
        ys = [chunk[1], chunk[3], chunk[4 + 1], chunk[6 + 1]]
        rects.append((min(xs), page_height - max(ys), max(xs), page_height - min(ys)))
    return rects


def normalize_rect(raw: str, page_height: float) -> tuple[float, float, float, float] | None:
    nums = [float(x) for x in raw.split()]
    if len(nums) < 4:
        return None
    return (nums[0], page_height - nums[3], nums[2], page_height - nums[1])


def build_annotations(pdf_path: Path, text_pdf_path: Path | None = None) -> list[Annotation]:
    raw_bytes = pdf_path.read_bytes()
    objects = load_all_objects(raw_bytes)
    page_order = collect_page_order(objects)
    page_map = {obj_num: idx + 1 for idx, obj_num in enumerate(page_order)}

    source_pdf = text_pdf_path or pdf_path
    page_words, page_lines, page_heights = load_pages_from_bbox(source_pdf)

    annots: list[Annotation] = []
    for obj_num, obj_body in sorted(objects.items()):
        obj_text = obj_body.decode("latin1", errors="ignore")
        subtype_match = SUBTYPE_RE.search(obj_text)
        subtype = subtype_match.group(1) if subtype_match else ""
        if subtype not in {"Highlight", "Text"}:
            continue
        parent = PARENT_RE.search(obj_text)
        quads = QUAD_RE.search(obj_text)
        rect_match = RECT_RE.search(obj_text)
        if not parent:
            continue
        page_ref = int(parent.group(1))
        page_num = page_map.get(page_ref)
        if not page_num:
            continue
        comment_raw = extract_field(obj_text, "RC") or extract_field(obj_text, "Contents") or ""
        comment = clean_comment(comment_raw)
        if quads:
            rects = normalize_quads(quads.group(1), page_heights[page_num])
        elif rect_match:
            rect = normalize_rect(rect_match.group(1), page_heights[page_num])
            rects = [rect] if rect else []
        else:
            rects = []
        if not rects:
            continue
        words = page_words.get(page_num, [])
        lines = page_lines.get(page_num, [])

        hit_words: list[Word] = []
        hit_lines: list[Line] = []
        for rect in rects:
            hit_words.extend(words_in_rect(words, rect))
            hit_lines.extend(lines_near_rect(lines, rect))
        unique_words = {(w.x_min, w.y_min, w.text): w for w in hit_words}
        unique_lines = {(l.x_min, l.y_min, l.text): l for l in hit_lines}
        if not unique_lines and subtype == "Text":
            fallback_lines = []
            for rect in rects:
                fallback_lines.extend(nearest_lines(lines, rect))
            unique_lines = {(l.x_min, l.y_min, l.text): l for l in fallback_lines}
        sorted_lines = sorted(unique_lines.values(), key=lambda l: (l.y_min, l.x_min))
        target = join_words_with_layout(list(unique_words.values()))
        if not target and sorted_lines and subtype == "Text":
            target = sorted_lines[0].text
        context = " / ".join(l.text for l in sorted_lines[:3]).strip()
        sort_y = min((r[1] for r in rects), default=0.0)
        annots.append(
            Annotation(
                obj_num=obj_num,
                page_ref=page_ref,
                page_num=page_num,
                comment=comment,
                quads=rects,
                target=target,
                context=context,
                sort_y=sort_y,
            )
        )
    annots.sort(key=lambda a: (a.page_num, a.sort_y))
    return annots


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--text-pdf", type=Path, default=None)
    parser.add_argument("--format", choices=["text", "markdown"], default="text")
    args = parser.parse_args()

    annots = build_annotations(args.pdf, args.text_pdf)
    if args.format == "markdown":
        print("| page | target | comment | context |")
        print("| --- | --- | --- | --- |")
        for a in annots:
            target = a.target.replace("|", "\\|")
            comment = a.comment.replace("\n", " / ").replace("|", "\\|")
            context = a.context.replace("|", "\\|")
            print(f"| {a.page_num} | {target} | {comment} | {context} |")
    else:
        for a in annots:
            print(f"[p.{a.page_num}] target: {a.target or '(no target text)'}")
            print(f"comment: {a.comment or '(no comment)'}")
            if a.context:
                print(f"context: {a.context}")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
