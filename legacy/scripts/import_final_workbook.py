from pathlib import Path
import json
import re

SOURCE = Path(r"C:\성균관대\10_학교\JEAN\경전 족보\경영전략_통합문제집_해설.md")
OUTPUT = Path("data/questions.js")

EXAMS = {
    "Ⅰ": {"id": "2023-2-icam", "label": "2023-2 아캠 족보", "year": 2023, "term": "2학기", "status": "63문항 완성"},
    "Ⅱ": {"id": "2024-1-final", "label": "2024-1 기말", "year": 2024, "term": "1학기 기말", "status": "60문항 완성"},
    "Ⅲ": {"id": "2025-1-final", "label": "2025-1 기말", "year": 2025, "term": "1학기 기말", "status": "46문항 완성"},
}


def normalize(value):
    value = re.sub(r"\*\*|\(정정\)", "", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value


def choice_value(line):
    value = line[2:].strip()
    parts = re.split(r"\s+/\s+(?=[A-E]\.)|\s+/\s+", value)
    return [normalize(part) for part in parts if part.strip()]


def find_answer(answer_text, choices):
    answer = normalize(answer_text)
    letter = re.match(r"^([A-Ea-e])(?:[.)\s]|$)", answer)
    if letter:
        index = ord(letter.group(1).upper()) - ord("A")
        if index < len(choices):
            return index
    number = re.match(r"^([1-5])번", answer)
    if number:
        index = int(number.group(1)) - 1
        if index < len(choices):
            return index
    for index, choice in enumerate(choices):
        clean_choice = re.sub(r"^[A-Ea-e][.)]\s*", "", normalize(choice))
        if answer == clean_choice or answer in clean_choice or clean_choice in answer:
            return index
    return 0


text = SOURCE.read_text(encoding="utf-8")
section_pattern = re.compile(r"^# ([ⅠⅡⅢ])\.\s+(.+?)$", re.M)
sections = list(section_pattern.finditer(text))
questions = []

for section_index, section in enumerate(sections):
    roman = section.group(1)
    exam = EXAMS[roman]
    end = sections[section_index + 1].start() if section_index + 1 < len(sections) else len(text)
    content = text[section.end():end]
    matches = list(re.finditer(r"^##\s+(\d+)\.\s+(.+?)$", content, re.M))
    for index, match in enumerate(matches):
        number = int(match.group(1))
        question = normalize(match.group(2))
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        block = content[match.end():block_end]
        choices = []
        for line in block.splitlines():
            if line.startswith("- "):
                choices.extend(choice_value(line))
        answer_match = re.search(r"\*\*정답:\s*(.*?)\*\*", block)
        explanation_match = re.search(r"\*\*해설:\*\*\s*(.*?)(?=\n---|\Z)", block, re.S)
        if not answer_match or not explanation_match or len(choices) < 2:
            continue
        answer_text = normalize(answer_match.group(1))
        explanation = normalize(explanation_match.group(1))
        questions.append({
            "id": f"{exam['id']}-{number:03}",
            "examId": exam["id"],
            "exam": exam["label"],
            "year": exam["year"],
            "term": exam["term"],
            "number": number,
            "question": question,
            "choices": choices,
            "answer": find_answer(answer_text, choices),
            "answerText": answer_text,
            "explanation": explanation,
        })

catalog = sorted(EXAMS.values(), key=lambda exam: -exam["year"])
questions.sort(key=lambda q: (-q["year"], q["examId"], q["number"]))
payload = "window.EXAM_CATALOG = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n\n"
payload += "window.QUESTION_BANK = " + json.dumps(questions, ensure_ascii=False, indent=2) + ";\n"
OUTPUT.write_text(payload, encoding="utf-8")

counts = {exam["label"]: sum(q["examId"] == exam["id"] for q in questions) for exam in catalog}
print(json.dumps({"total": len(questions), "counts": counts}, ensure_ascii=False))
