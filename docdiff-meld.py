#!/usr/bin/env python3

import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def inline_text(inlines):
    out = []

    if inlines is None:
        return ""

    if isinstance(inlines, str):
        return inlines

    if isinstance(inlines, dict):
        inlines = [inlines]

    if not isinstance(inlines, list):
        return ""

    for item in inlines:
        if isinstance(item, list):
            out.append(inline_text(item))
            continue

        if not isinstance(item, dict):
            continue

        t = item.get("t")
        c = item.get("c")

        if t == "Str":
            out.append(str(c))
        elif t == "Space":
            out.append(" ")
        elif t in {"SoftBreak", "LineBreak"}:
            out.append(" ")
        elif t in {
            "Emph",
            "Strong",
            "Strikeout",
            "Superscript",
            "Subscript",
            "SmallCaps",
        }:
            out.append(inline_text(c))
        elif t == "Quoted":
            out.append(inline_text(c[1] if isinstance(c, list) and len(c) > 1 else c))
        elif t in {"Link", "Image"}:
            out.append(inline_text(c[1] if isinstance(c, list) and len(c) > 1 else c))
        elif t == "Code":
            out.append(str(c[1] if isinstance(c, list) and len(c) > 1 else c))
        elif t == "Math":
            out.append(str(c[1] if isinstance(c, list) and len(c) > 1 else c))
        elif isinstance(c, list):
            out.append(inline_text(c))

    return "".join(out)


def block_text(block):
    t = block.get("t")
    c = block.get("c")

    if t in {"Para", "Plain"}:
        return [inline_text(c).strip()]

    if t == "Header":
        return [inline_text(c[2]).strip()]

    if t == "BulletList":
        lines = []
        for item in c:
            for b in item:
                txts = block_text(b)
                for txt in txts:
                    if txt:
                        lines.append("- " + txt)
        return lines

    if t == "OrderedList":
        lines = []
        for i, item in enumerate(c[1], 1):
            for b in item:
                txts = block_text(b)
                for txt in txts:
                    if txt:
                        lines.append(f"{i}. {txt}")
        return lines

    if t == "BlockQuote":
        lines = []
        for b in c:
            lines.extend(block_text(b))
        return lines

    if t == "Table":
        # Pandoc tables are horrible structurally, but this recursive fallback
        # extracts cell text without ASCII borders or | | junk.
        return extract_any_text(c)

    if isinstance(c, list):
        return extract_any_text(c)

    return []


def extract_any_text(obj):
    lines = []

    if isinstance(obj, dict):
        if "t" in obj:
            lines.extend(block_text(obj))
        else:
            for v in obj.values():
                lines.extend(extract_any_text(v))

    elif isinstance(obj, list):
        # Inline list?
        if obj and all(isinstance(x, dict) and "t" in x for x in obj):
            txt = inline_text(obj).strip()
            if txt:
                lines.append(txt)
        else:
            for v in obj:
                lines.extend(extract_any_text(v))

    return lines


def pandoc_json(path: Path):
    result = subprocess.run(
        ["pandoc", str(path), "-t", "json"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        sys.exit(f"Pandoc failed on {path}:\n{result.stderr}")

    return json.loads(result.stdout)


def clean_lines(lines):
    cleaned = []

    for line in lines:
        line = " ".join(line.split())

        if not line:
            continue

        # Skip likely empty template artifacts
        if set(line) <= {"-", "_", ".", " "}:
            continue

        wrapped = textwrap.fill(line, width=100)
        cleaned.append(wrapped)

    return "\n\n".join(cleaned) + "\n"


def convert(path: Path) -> str:
    doc = pandoc_json(path)
    lines = []

    for block in doc.get("blocks", []):
        lines.extend(block_text(block))

    return clean_lines(lines)


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: docdiff-meld old.docx new.docx")

    if not shutil.which("pandoc"):
        sys.exit("Error: pandoc is not installed. Try: sudo apt install pandoc")

    if not shutil.which("meld"):
        sys.exit("Error: meld is not installed. Try: sudo apt install meld")

    file1 = Path(sys.argv[1]).expanduser().resolve()
    file2 = Path(sys.argv[2]).expanduser().resolve()

    for f in (file1, file2):
        if not f.exists():
            sys.exit(f"File not found: {f}")
        if f.suffix.lower() not in {".docx", ".odt"}:
            sys.exit(f"Unsupported file type: {f.suffix}")

    tmpdir = Path(tempfile.mkdtemp(prefix="docdiff-meld-"))

    out1 = tmpdir / f"{file1.stem}.clean.txt"
    out2 = tmpdir / f"{file2.stem}.clean.txt"

    out1.write_text(convert(file1), encoding="utf-8")
    out2.write_text(convert(file2), encoding="utf-8")

    print(f"Wrote:\n  {out1}\n  {out2}")
    subprocess.run(["meld", str(out1), str(out2)])


if __name__ == "__main__":
    main()
