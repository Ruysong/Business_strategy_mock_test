from pathlib import Path
import json
import re
import subprocess

ROOT = Path("ocr-md")

# Concept-based answer keys. These are used only for readable questions.
KEYS = {
    "2023-1-mid": [3,0,2,2,4,1,1,1,0,0,1,2,0,3,0,1,2,3,0,1,3,1,2,1,1,1,0,1,1,2,1,1,0],
    "2023-1-final": [3,1,1,2,2,0,3,1,1,0,0,3,0,1,0,0,1],
    "2021-2-final": [0,1,1,1,1,0,1,1,2,2,2,1,3,3,2,3,1,1,0,1,0,0,1,0,1,0],
}

SOURCES = [
    ("2023-1-mid", 2023, "1학기 중간", "23-1 중간.md"),
    ("2023-1-final", 2023, "1학기 기말", "23-1 기말.md"),
    ("2021-2-final", 2021, "2학기 기말", "21-2 기말 (답x).md"),
]


def clean(text):
    text = re.sub(r"^#.*?$|^- 원본:.*?$|^- 총 페이지:.*?$", "", text, flags=re.M)
    text = re.sub(r"^## 페이지 \d+.*?$|<!--.*?-->", "", text, flags=re.M)
    text = re.sub(r"Downloaded by.*|lOMoARcPSD\|\d+|이 문제에 플래그를 지정|답변 선택 그룹", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def blocks(text):
    matches = list(re.finditer(r"문제\s*(\d+)(?:\s*1점)?", text))
    result = []
    for i, match in enumerate(matches):
        number = int(match.group(1))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result.append((number, clean(text[match.end():end])))
    return result


def split_question_choices(body):
    # T/F questions are unambiguous.
    tf = re.search(r"\s참\s+거짓\s*$", body)
    if tf:
        return body[:tf.start()].strip(), ["참", "거짓"]

    # Multiple-choice OCR lacks bullets. Sentence-ending punctuation gives a useful
    # boundary; retain 4-5 trailing statements as choices.
    chunks = [x.strip() for x in re.split(r"(?<=[.?])\s+", body) if x.strip()]
    if len(chunks) >= 5:
        choice_count = 5 if len(chunks) >= 6 else 4
        return " ".join(chunks[:-choice_count]).strip(), chunks[-choice_count:]
    return "", []


def explanation(question, choices, answer):
    selected = choices[answer] if 0 <= answer < len(choices) else ""
    if len(choices) == 2 and choices == ["참", "거짓"]:
        return "문장의 핵심 전략 개념과 사례 설명을 기준으로 판단한 정답이다."
    return f"핵심 개념에 가장 부합하는 설명은 ‘{selected}’이다."


questions = []
for key, year, term, filename in SOURCES:
    text = clean((ROOT / filename).read_text(encoding="utf-8"))
    answers = KEYS[key]
    for number, body in blocks(text):
        if number < 1 or number > len(answers):
            continue
        question, choices = split_question_choices(body)
        if not question or len(choices) < 2:
            continue
        answer = answers[number - 1]
        if answer >= len(choices):
            continue
        questions.append({
            "id": f"{key}-{number:03}",
            "year": year,
            "term": term,
            "number": number,
            "question": question,
            "choices": choices,
            "answer": answer,
            "explanation": explanation(question, choices, answer),
            "source": filename,
        })

# Preserve the existing high-confidence 2020-2 and 2022-2 generated questions.
generated = subprocess.check_output(
    ["git", "show", "HEAD:data/generated-questions.js"], text=True, encoding="utf-8"
)
payload = generated.split("=", 1)[1].strip().rstrip(";")
questions.extend(json.loads(payload))
questions.sort(key=lambda q: (-q["year"], q["term"], q["number"]))

out = "// Clear readable past-exam questions only. Auto-generated.\nwindow.QUESTION_BANK = "
out += json.dumps(questions, ensure_ascii=False, indent=2) + ";\n"
Path("data/questions.js").write_text(out, encoding="utf-8")
print(f"clear bank: {len(questions)} questions")
