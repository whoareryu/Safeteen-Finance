---
name: code-review
description: 이 저장소(fastapi+www+flutter) 기준으로 코드 리뷰를 수행합니다. 버그, 보안, 성능뿐 아니라 헥사고날/스타 토폴로지 규칙 위반도 검토합니다.
---

## 코드 리뷰 수행

리뷰 전 루트 `CLAUDE.md`와 변경된 도메인의 하위 `CLAUDE.md`
(`fastapi/CLAUDE.md` / `www/CLAUDE.md` / `flutter/CLAUDE.md`)를 먼저 읽는다.

### 검토 항목

1. **버그 및 논리 오류**: 잠재적 버그, 엣지 케이스 누락
2. **보안**: 시크릿 하드코딩(`secret_manager` 경유 여부), SQL 인젝션, XSS
3. **성능**: 불필요한 반복, N+1 쿼리, 메모리 누수
4. **코드 품질**: 함수 길이, 중복 코드, 명명 규칙
5. **이 저장소 고유 규칙**:
   - `fastapi`: SOLID/헥사고날 레이어 경계, spoke→spoke 직접 임포트 금지(`ontology`
     허브만 경유), `get_{feature}_use_case` 네이밍, `Depends()`만으로 의존성 주입했는지
   - `www`: `any` 사용 여부, `components/ui/` 직접 수정 여부, 컴포넌트에서 직접
     `fetch` 호출 여부(`.claude/rules/typescript.md` §9)
   - 루트 `CLAUDE.md` §3 "정밀한 수정" — 요청 범위를 벗어난 리팩터링이 섞여 있는지

### 출력 형식

각 문제는 다음 형식으로 보고한다.

- **심각도**: 높음/중간/낮음
- **위치**: 파일명과 줄 번호
- **문제**: 무엇이 잘못되었는지
- **개선안**: 어떻게 고칠 수 있는지
