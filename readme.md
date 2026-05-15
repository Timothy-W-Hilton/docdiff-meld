# docdiff-meld

Readable side-by-side diffs for `.docx` and `.odt` documents on Linux.

`docdiff-meld` converts two office documents into cleaned semantic text, then opens the result in [Meld](https://meldmerge.org/) for side-by-side comparison.

The goal is to review meaningful prose changes without being overwhelmed by:

- Word tracked-changes markup
- XML/layout noise
- table formatting artifacts
- whitespace churn
- line wrapping differences

---

# Why?

Word and LibreOffice change tracking become difficult to read for large edits, especially when deletions are shown with strikethrough.

Diffing `.docx` or `.odt` directly is also not useful because those formats contain large amounts of formatting and layout metadata.

This tool instead asks:

> What changed in the actual text?

---

# Features

- Supports `.docx` and `.odt`
- Extracts semantic text using Pandoc
- Removes most formatting-only noise
- Suppresses table-layout artifacts such as `| |`
- Normalizes whitespace
- Preserves paragraph structure
- Opens cleaned output directly in Meld
- Linux-native workflow
- No Microsoft Office required

---

# Requirements

Install dependencies:

```bash
sudo apt install pandoc meld
```

Python 3 is also required.

---

# Installation

Clone the repository:

```bash
git clone <repo-url>
cd docdiff-meld
```

Make the script executable:

```bash
chmod +x docdiff-meld.py
```

Optional: install globally:

```bash
sudo cp docdiff-meld.py /usr/local/bin/docdiff-meld
```

---

# Usage

```bash
docdiff-meld old.docx new.docx
```

or:

```bash
docdiff-meld old.odt new.odt
```

Mixed formats also work:

```bash
docdiff-meld old.docx new.odt
```

The script creates cleaned temporary `.txt` files and opens them in Meld.

---

# Recommended Meld settings

Enable visual line wrapping:

```text
☰ Menu → Preferences → Editor → Wrap text
```

The script keeps each paragraph as a single logical line so that reflowed text and newline changes are not treated as meaningful diffs.

Meld's visual wrapping then makes long paragraphs readable without introducing whitespace-only differences.

---

# What this tool ignores

This tool intentionally ignores or simplifies:

- formatting changes
- style changes
- comments
- tracked-change metadata
- page layout
- headers/footers
- exact table structure
- images and figures

It is designed for reviewing prose edits, not final formatting validation.

---

# Suggested workflow

When collaborators send revised office documents:

```bash
docdiff-meld previous.docx revised.docx
```

Review semantic changes in Meld.

Then, if necessary, inspect final formatting separately in LibreOffice or Word Online.

---

# License

MIT License.


