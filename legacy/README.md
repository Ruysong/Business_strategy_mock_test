# 경전 기출 플래시카드

Vercel에 바로 배포할 수 있는 정적 PWA입니다. iPad와 모바일에서 사용할 수 있고 풀이 기록, 오답, 별표는 브라우저 `localStorage`에 저장됩니다.

정제된 통합문제집 기준 10개 독립 시험, 총 394문항을 제공합니다. 연도와 시험명이 같아도 내용이 다른 시험지는 별도 회차로 구분하며, 모든 문항에 선지, 정답, 해설이 포함되어 있습니다.

## 문제 추가

`data/questions.js`의 `window.QUESTION_BANK` 배열에 문제를 추가합니다.

```js
{
  id: "2025-final-001",
  year: 2025,
  term: "1학기 기말",
  number: 1,
  question: "문제",
  choices: ["선지 1", "선지 2", "선지 3", "선지 4"],
  answer: 0,
  explanation: "한 줄 해설"
}
```

`answer`는 0부터 시작합니다. 1번 선지가 정답이면 `0`, 4번 선지가 정답이면 `3`입니다.

## 원본 재추출

원본 파일이 갱신되면 아래 스크립트를 순서대로 실행합니다.

```powershell
python scripts/extract_sources.py
python scripts/build_question_bank.py
```

텍스트형 PDF는 자동 처리됩니다. 이미지 스캔형 PDF와 JPG는 별도 한글 OCR 처리가 필요합니다.

## 단축키

- `←` / `→`: 이전 / 다음 문제
- `1` ~ `4`: 답 선택
- `R`: 정답 취소 후 다시 풀기
- `S`: 별표

## 배포

Vercel에서 이 GitHub 저장소를 Import하면 별도 설정 없이 배포됩니다.
