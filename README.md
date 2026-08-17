# J&J SQLD 문제은행

SQLD 기출/복원 문제를 한 파일로 정리한 정적 문제은행입니다.

## 배포

Vercel에서 이 GitHub 저장소를 Import하면 루트 `index.html`이 그대로 배포됩니다. 별도 빌드 명령은 필요 없습니다.

## 파일 구조

- `index.html`: 현재 배포할 SQLD 문제은행
- `legacy/`: 이전 경전 기출 플래시카드 앱과 관련 데이터/스크립트 보관
- `vercel.json`: Vercel 정적 배포 설정
- `sw.js`: 이전 PWA 서비스워커 캐시 정리용 파일

## Legacy

예전 경전 기출 앱은 `legacy/index.html` 아래에 보관했습니다. 새 SQLD 문제은행 배포에는 사용하지 않습니다.
