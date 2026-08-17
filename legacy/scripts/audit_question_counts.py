from pathlib import Path
import re

ROOT = Path("ocr-md")


def candidates(text):
    patterns = [
        r"(?im)^\s*문제\s*(\d{1,3})\b",
        r"(?im)^\s*(\d{1,3})\s*[.)]\s+",
        r"(?im)^\s*(\d{1,3})\s*장\s*$",
    ]
    values = []
    for pattern in patterns:
        values.extend(int(x) for x in re.findall(pattern, text))
    return sorted(set(x for x in values if 0 < x <= 100))


lines = [
    "# 기출별 문항 수 감사",
    "",
    "> OCR/텍스트에서 문항 번호 패턴을 자동 탐지한 결과입니다. 스캔 품질이 낮은 자료는 실제 문항 수보다 적게 탐지될 수 있습니다.",
    "",
    "| 파일 | 탐지 문항 수 | 범위 | 누락 번호 후보 |",
    "|---|---:|---|---|",
]

for path in sorted(ROOT.glob("*.md")):
    if path.name == "README.md":
        continue
    text = path.read_text(encoding="utf-8")
    nums = candidates(text)
    if nums:
        missing = [x for x in range(min(nums), max(nums) + 1) if x not in nums]
        span = f"{min(nums)}-{max(nums)}"
        missing_text = ", ".join(map(str, missing)) or "없음"
    else:
        span = "-"
        missing_text = "번호 탐지 실패"
    lines.append(f"| {path.stem} | {len(nums)} | {span} | {missing_text} |")

Path("ocr-md/QUESTION-AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
