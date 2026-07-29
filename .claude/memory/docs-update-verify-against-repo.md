---
name: docs-update-verify-against-repo
description: 사용자가 붙여넣은 템플릿으로 문서를 갱신할 때는 항목 목차로만 쓰고 값은 저장소에서 검증해 채운다
metadata:
  type: feedback
---

문서(특히 CLAUDE.md) 갱신을 요청하며 다른 프로젝트나 다른 저장소에서 가져온
템플릿을 붙여넣는 경우가 있다. 이 저장소는 `fastapi`(FastAPI 백엔드) +
`www`(Next.js 프론트엔드) + `flutter`(모바일) 모노레포이므로, 다른 스택을
전제로 한 템플릿을 그대로 적용하면 존재하지 않는 명령어·디렉터리·모듈을
지시하는 문서가 된다.

**Why:** 템플릿을 그대로 붙이면 이 저장소에 없는 경로나 스택(예: 다른 패키지
매니저, 다른 테스트 프레임워크)을 지시하는 거짓 문서가 만들어진다. 사용자가
원하는 것은 대개 템플릿의 *내용*이 아니라 "이런 항목이 빠져 있다"는 *목차*다.

**How to apply:**
- 붙여넣은 내용은 **섹션 목록으로만** 취급한다. 각 항목의 값은 저장소를 직접
  읽어 채운다 (`fastapi/requirements.txt`, `www/package.json`,
  `docker-compose.yml`, `.env.example`, `git log`, `fastapi/apps/*` 등).
- 템플릿에 있으나 이 저장소에 실물이 없는 항목은 **넣지 않는다.** 대신
  실재하는 동종 항목으로 대체한다.
- 확인 불가능한 항목(예: 브랜치 전략)은 추측하지 말고 AskUserQuestion으로
  묻는다. 실제 git 상태를 근거로 선택지를 제시하면 판단이 빠르다.
- "기존 내용은 수정하지 마"라는 요청이 오면 문자 그대로 지킨다. 작업 후
  `git diff --stat`으로 `insertions`만 있고 `deletions`가 0인지 검증해 보고한다.

관련: [[subdoc-directory-names-verified]]
