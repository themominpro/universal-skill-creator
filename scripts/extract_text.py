#!/usr/bin/env python3
"""Extract plain text from .txt, .md, .docx, and simple .pdf files.

Optional fallback only, NOT a hard rule: Claude Code and Claude read
.md, .pdf, .docx, .ppt, and similar formats natively, so use harness
reading first. Use this script only when a harness or script needs
plain text, for example before build_domain_lexicon.py.

Usage: python3 scripts/extract_text.py <input> [--output <file>]
No external dependencies, so it works in a plain Python environment.
- .txt/.md: read as text.
- .docx: a .docx is a ZIP archive; extract text from word/document.xml
  paragraph runs, in document order.
- .pdf: extract text from uncompressed and zlib-compressed content
  streams, from Tj and TJ operators. This handles text-based PDFs.
  Scanned image-only PDFs have no text layer and will return a clear
  warning instead of invented text; those need OCR outside this script.
Exit 0 on success, 1 on unsupported type or no text found.
Output is the extracted text, or JSON with a warning for scanned PDFs.
"""
import argparse
import re
import sys
import zipfile
import zlib
from pathlib import Path
from xml.etree import ElementTree


def extract_docx(path):
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ElementTree.fromstring(xml)
    paragraphs = []
    for para in root.iter(f"{{{ns['w']}}}p"):
        runs = []
        for node in para.iter():
            if node.tag == f"{{{ns['w']}}}t" and node.text:
                runs.append(node.text)
            if node.tag == f"{{{ns['w']}}}tab":
                runs.append("\t")
        paragraphs.append("".join(runs))
    return "\n".join(paragraphs)


def _pdf_text_from_stream(data):
    # Try zlib decompression for FlateDecode streams, else use raw data.
    try:
        data = zlib.decompress(data)
    except Exception:
        pass
    text_parts = []
    # Tj: (text) Tj ; TJ: [(text) ...] TJ
    for match in re.finditer(rb"\((?:[^()\\]|\\.)*\)\s*Tj", data):
        raw = match.group(0)
        inner = raw[1:raw.rfind(b")")]
        inner = inner.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
        try:
            text_parts.append(inner.decode("utf-8", errors="ignore"))
        except Exception:
            continue
    for match in re.finditer(rb"\[((?:[^\[\]]|\[[^\]]*\])*)\]\s*TJ", data):
        block = match.group(1)
        for part in re.findall(rb"\((?:[^()\\]|\\.)*\)", block):
            inner = part[1:-1].replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
            text_parts.append(inner.decode("utf-8", errors="ignore"))
    return " ".join(text_parts)


def extract_pdf(path):
    raw = Path(path).read_bytes()
    chunks = []
    for match in re.finditer(rb"stream\r?\n(.*?)endstream", raw, flags=re.DOTALL):
        chunk = _pdf_text_from_stream(match.group(1))
        if chunk.strip():
            chunks.append(chunk)
    text = "\n".join(chunks).strip()
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output")
    args = parser.parse_args()
    path = Path(args.input)
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md", ".markdown"):
        text = path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".docx":
        text = extract_docx(path)
    elif suffix == ".pdf":
        text = extract_pdf(path)
        if not text:
            print("WARNING: no text layer found. This PDF is likely scanned image-only and needs OCR; no text was invented.", file=sys.stderr)
            return 1
    else:
        print(f"unsupported type: {suffix}", file=sys.stderr)
        return 1
    text = text.strip()
    if not text:
        print("no text found in input", file=sys.stderr)
        return 1
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
