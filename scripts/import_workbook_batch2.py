from pathlib import Path
import json
import re
import subprocess

SOURCE = Path(r"C:\성균관대\10_학교\JEAN\경전 족보\files\경영전략_통합문제집2_해설.md")
OUTPUT = Path("data/questions.js")
NODE = r"C:\Users\rruys\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"

EXAMS = {
    "Ⅴ": {"id": "2020-2-final-unified", "label": "20-2 기말 · 통합본", "year": 2020, "term": "2학기 기말", "status": "44문항 완성"},
    "Ⅵ": {"id": "2021-2-final-korean", "label": "21-2 기말 · 한글", "year": 2021, "term": "2학기 기말", "status": "26문항 완성"},
    "Ⅶ": {"id": "2022-1-final-icam", "label": "22-1 기말 · 아캠 족보", "year": 2022, "term": "1학기 기말", "status": "36문항 완성"},
}


def normalize(value):
    value = re.sub(r"\*\*|\([^)]*원본[^)]*\)|\([^)]*응시자[^)]*\)", "", value)
    return re.sub(r"\s+", " ", value).strip(" .")


def parse_choices(block):
    choices = []
    for line in block.splitlines():
        if line.startswith("- "):
            choices.extend(normalize(x) for x in re.split(r"\s+/\s+", line[2:]) if x.strip())
    return choices


def answer_index(answer_text, choices):
    answer = normalize(answer_text)
    letter = re.match(r"^([A-Ea-e])(?:[.)\s]|$)", answer)
    if letter:
        index = ord(letter.group(1).upper()) - ord("A")
        if index < len(choices):
            return index
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
new_ids = {exam["id"] for exam in EXAMS.values()}
catalog = [exam for exam in existing["catalog"] if exam["id"] not in new_ids]
questions = [q for q in existing["questions"] if q["examId"] not in new_ids]

text = SOURCE.read_text(encoding="utf-8")
sections = list(re.finditer(r"^# ([ⅤⅥⅦ])\.\s+(.+?)$", text, re.M))
for si, section in enumerate(sections):
    exam = EXAMS[section.group(1)]
    end = sections[si + 1].start() if si + 1 < len(sections) else len(text)
    content = text[section.end():end]
    matches = list(re.finditer(r"^##\s+(\d+)\.\s+(.+?)$", content, re.M))
    for mi, match in enumerate(matches):
        block_end = matches[mi + 1].start() if mi + 1 < len(matches) else len(content)
        block = content[match.end():block_end]
        answer = re.search(r"\*\*정답:\s*(.*?)\*\*", block)
        explanation = re.search(r"\*\*해설:\*\*\s*(.*?)(?=\n---|\Z)", block, re.S)
        choices = parse_choices(block)
        if not answer or not explanation or len(choices) < 2:
            continue
        number = int(match.group(1))
        answer_text = normalize(answer.group(1))
        questions.append({
            "id": f"{exam['id']}-{number:03}", "examId": exam["id"], "exam": exam["label"],
            "year": exam["year"], "term": exam["term"], "number": number,
            "question": normalize(match.group(2)), "choices": choices,
            "answer": answer_index(answer_text, choices), "answerText": answer_text,
            "explanation": normalize(explanation.group(1)),
        })

catalog.extend(EXAMS.values())
catalog.sort(key=lambda e: (-e["year"], e["label"]))
questions.sort(key=lambda q: (-q["year"], q["examId"], q["number"]))
OUTPUT.write_text(
    "window.EXAM_CATALOG = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n\n"
    + "window.QUESTION_BANK = " + json.dumps(questions, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
print(json.dumps({"total": len(questions), "new": {e["label"]: sum(q["examId"] == e["id"] for q in questions) for e in EXAMS.values()}}, ensure_ascii=False))
