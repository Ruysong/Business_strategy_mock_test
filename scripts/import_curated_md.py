from pathlib import Path
import json
import re
import subprocess

SOURCE = Path(r"C:\성균관대\10_학교\JEAN\경전 족보\경영전략_25-1_46문제_답안_해설.md")
BANK = Path("data/questions.js")

text = SOURCE.read_text(encoding="utf-8")
pattern = re.compile(
    r"## 문제\s+(\d+)\s+"
    r"\*\*문제:\*\*\s*(.*?)\s+"
    r"\*\*답:\*\*\s*(.*?)\s+"
    r"\*\*해설:\*\*\s*(.*?)(?=\n---|\Z)",
    re.S,
)

current = BANK.read_text(encoding="utf-8")
catalog = [
    {"id": "2025-1-final", "label": "25-1 기말", "year": 2025, "term": "1학기 기말", "status": "46문항 완성"},
    {"id": "2024-1-final", "label": "24-1 기말", "year": 2024, "term": "1학기 기말", "status": "정답표만 보유"},
    {"id": "2023-2-final", "label": "23-2", "year": 2023, "term": "2학기", "status": "일부 복원"},
    {"id": "2023-2-offline", "label": "23-2 오프라인 족보", "year": 2023, "term": "2학기 오프라인", "status": "OCR 불명확"},
]
node_script = (
    "global.window={};require('./data/questions.js');"
    "console.log(JSON.stringify(window.QUESTION_BANK))"
)
node = r"C:\Users\rruys\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
existing = json.loads(subprocess.check_output([node, "-e", node_script], text=True, encoding="utf-8"))
questions = [q for q in existing if q.get("examId") != "2025-1-final"]

for match in pattern.finditer(text):
    number = int(match.group(1))
    question = re.sub(r"\s+", " ", match.group(2)).strip()
    answer_text = re.sub(r"\s+", " ", match.group(3)).strip()
    explanation = re.sub(r"\s+", " ", match.group(4)).strip()
    questions.append({
        "id": f"2025-1-final-{number:03}",
        "examId": "2025-1-final",
        "exam": "25-1 기말",
        "year": 2025,
        "term": "1학기 기말",
        "number": number,
        "question": question,
        "choices": [],
        "answer": 0,
        "answerText": answer_text,
        "explanation": explanation,
    })

questions.sort(key=lambda q: (-q["year"], q["examId"], q["number"]))
output = "window.EXAM_CATALOG = " + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n\n"
output += "window.QUESTION_BANK = " + json.dumps(questions, ensure_ascii=False, indent=2) + ";\n"
BANK.write_text(output, encoding="utf-8")
print(f"Imported 25-1: {sum(q['examId'] == '2025-1-final' for q in questions)} questions")
