from pathlib import Path
import re

SOURCE = Path(r"C:\성균관대\10_학교\JEAN\경전 족보\경전 족보")
OUTPUT = Path("ocr-md")
LATEST_STEMS = {"23-2", "경전 23-2 (오프) 족보", "경전 24-1 기말", "경전 25-1 기말"}
rows = []

for source in sorted(SOURCE.iterdir()):
    if source.stem not in LATEST_STEMS:
        continue
    md = OUTPUT / f"{source.stem}.md"
    text = md.read_text(encoding="utf-8") if md.exists() else ""
    pages = len(re.findall(r"^## 페이지 \d+", text, re.M))
    if source.suffix.lower() == ".docx":
        pages = max(1, pages)
    rows.append((source.name, md.name if md.exists() else "누락", pages, len(text)))

lines = [
    "# 전체 OCR 문서 목록",
    "",
    f"- 원본 파일 수: {len(rows)}",
    f"- 생성된 Markdown 수: {sum(1 for _, name, _, _ in rows if name != '누락')}",
    "",
    "| 원본 | Markdown | 페이지/섹션 | 글자 수 |",
    "|---|---|---:|---:|",
]
for source, md, pages, chars in rows:
    lines.append(f"| {source} | [{md}](<{md}>) | {pages} | {chars} |")

(OUTPUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
