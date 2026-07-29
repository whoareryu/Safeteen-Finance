---
name: subdoc-directory-names-verified
description: fastapi/www/flutter 하위 CLAUDE.md는 코드네임이 아니라 실제 디렉터리명을 그대로 쓴다 — 확인됨, 문제 없음
metadata:
  type: project
---

2026-07-29 확인: 이 저장소의 하위 CLAUDE.md들은 실제 디렉터리명을 코드네임
없이 그대로 제목에 쓴다.

- `fastapi/CLAUDE.md:1` `# CLAUDE.md — Backend (whoareryu)`
- `www/CLAUDE.md:1` `# CLAUDE.md — Frontend (www)`
- `flutter/CLAUDE.md:1` `# CLAUDE.md — Mobile (flutter)`

**Why:** 다른 저장소에서는 하위 CLAUDE.md가 실제 디렉터리 경로 대신 코드네임을
써서 `cd <코드네임>` 같은 동작하지 않는 명령어를 안내하는 문제가 있었다. 이
저장소에는 그런 코드네임이 없으므로 동일한 문제가 발생하지 않는다.

**How to apply:** 새 하위 CLAUDE.md를 추가하거나 기존 문서에서 `cd <경로>`
같은 명령어를 볼 때는, 그 경로가 실제 최상위 디렉터리(`fastapi`/`www`/
`flutter`)와 일치하는지만 확인하면 된다. 코드네임과 경로를 분리해서 판단할
필요는 없다.

관련: [[docs-update-verify-against-repo]]
