# 경전 기출 플래시카드

Vercel에 바로 배포할 수 있는 정적 PWA입니다. iPad와 모바일에서 사용할 수 있고 풀이 기록, 오답, 별표는 브라우저 `localStorage`에 저장됩니다.

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

## 단축키

- `←` / `→`: 이전 / 다음 문제
- `1` ~ `4`: 답 선택
- `R`: 정답 취소 후 다시 풀기
- `S`: 별표

## 배포

Vercel에서 이 GitHub 저장소를 Import하면 별도 설정 없이 배포됩니다.
