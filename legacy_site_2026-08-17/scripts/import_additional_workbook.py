from pathlib import Path
import json
import re
import subprocess

SOURCE = Path(r"C:\성균관대\10_학교\JEAN\경전 족보\경영전략_통합문제집_해설 2.md")
OUTPUT = Path("data/questions.js")
NODE = r"C:\Users\rruys\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"

EXAMS = {
    "Ⅰ": {"id": "2022-2-icam-marked", "label": "22-2 기말 · 아캠 답표기본", "year": 2022, "term": "2학기 기말", "status": "34문항 완성"},
    "Ⅱ": {"id": "2023-1-mid", "label": "23-1 중간", "year": 2023, "term": "1학기 중간", "status": "34문항 완성"},
    "Ⅲ": {"id": "2023-1-final", "label": "23-1 기말", "year": 2023, "term": "1학기 기말", "status": "17문항 완성"},
    "Ⅳ": {"id": "2022-2-question-only", "label": "22-2 기말 · 문제만 별개 시험지", "year": 2022, "term": "2학기 기말", "status": "34문항 완성"},
}


def normalize(value):
    value = re.sub(r"\*\*|\([^)]*원 시험지[^)]*\)|\([^)]*보너스[^)]*\)", "", value)
    return re.sub(r"\s+", " ", value).strip(" .")


def choices_from(block):
    choices = []
    for line in block.splitlines():
        if line.startswith("- "):
            choices.extend(normalize(x) for x in re.split(r"\s+/\s+", line[2:]) if x.strip())
    return choices


def find_answer(answer_text, choices):
    answer = normalize(answer_text)
    letter = re.match(r"^([A-Ea-e])(?:[.)\s]|$)", answer)
    if letter and ord(letter.group(1).upper()) - ord("A") < len(choices):
        return ord(letter.group(1).upper()) - ord("A")
    number = re.match(r"^([1-5])번", answer)
    if number and int(number.group(1)) <= len(choices):
        return int(number.group(1)) - 1
    for index, choice in enumerate(choices):
        clean = re.sub(r"^[A-Ea-e][.)]\s*", "", normalize(choice))
        if answer == clean or answer in clean or clean in answer:
            return index
    return 0


node_script = "global.window={};require('./data/questions.js');console.log(JSON.stringify({catalog:window.EXAM_CATALOG,questions:window.QUESTION_BANK}))"
existing = json.loads(subprocess.check_output([NODE, "-e", node_script], text=True, encoding="utf-8"))
catalog = [exam for exam in existing["catalog"] if exam["id"] not in {e["id"] for e in EXAMS.values()}]
questions = [q for q in existing["questions"] if q["examId"] not in {e["id"] for e in EXAMS.values()}]

text = SOURCE.read_text(encoding="utf-8")
sections = list(re.finditer(r"^# ([ⅠⅡⅢⅣ])\.\s+(.+?)$", text, re.M))
for si, section in enumerate(sections):
    exam = EXAMS[section.group(1)]
    end = sections[si + 1].start() if si + 1 < len(sections) else len(text)
    content = text[section.end():end]
    matches = list(re.finditer(r"^##\s+(\d+)\.\s+(.+?)$", content, re.M))
    for mi, match in enumerate(matches):
        number = int(match.group(1))
        end_block = matches[mi + 1].start() if mi + 1 < len(matches) else len(content)
        block = content[match.end():end_block]
        answer_match = re.search(r"\*\*정답:\s*(.*?)\*\*", block)
        explanation_match = re.search(r"\*\*해설:\*\*\s*(.*?)(?=\n---|\Z)", block, re.S)
        choices = choices_from(block)
        if not answer_match or not explanation_match or len(choices) < 2:
            continue
        answer_text = normalize(answer_match.group(1))
        questions.append({
            "id": f"{exam['id']}-{number:03}", "examId": exam["id"], "exam": exam["label"],
            "year": exam["year"], "term": exam["term"], "number": number,
            "question": normalize(match.group(2)), "choices": choices,
            "answer": find_answer(answer_text, choices), "answerText": answer_text,
            "explanation": normalize(explanation_match.group(1)),
        })

catalog.extend(EXAMS.values())
catalog.sort(key=lambda e: (-e["year"], e["label"]))
questions.sort(key=lambda q: (-q["year"], q["examId"], q["number"]))
payload = "window.EXAM_CATALOG = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n\n"
payload += "window.QUESTION_BANK = " + json.dumps(questions, ensure_ascii=False, indent=2) + ";\n"
OUTPUT.write_text(payload, encoding="utf-8")
print(json.dumps({"total": len(questions), "new": {e["label"]: sum(q["examId"] == e["id"] for q in questions) for e in EXAMS.values()}}, ensure_ascii=False))
