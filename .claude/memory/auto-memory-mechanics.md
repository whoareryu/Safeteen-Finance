---
name: auto-memory-mechanics
description: 자동 메모리 동작 방식 — MEMORY.md는 첫 200줄만 자동 로드되고 주제 파일은 필요할 때만 읽힌다
metadata:
  type: reference
---

Claude Code 자동 메모리의 로딩 규칙과 활성화 설정. (출처: Claude Code 문서)

## 로딩 규칙

- `MEMORY.md`의 **첫 200줄**이 매 세션 시작 시 시스템 프롬프트에 자동 로드된다.
- 200줄을 초과하는 내용은 자동 로드되지 않는다. 필요할 때 Claude가 직접 읽는다.
- 상세 내용은 `debugging.md`, `patterns.md`처럼 **별도 주제 파일로 분리**한다.
- 주제 파일은 필요할 때만 읽힌다. 세션 시작 시 전부 로드되지 않는다.
- **200줄 제한은 `MEMORY.md`에만 적용된다.**

## CLAUDE.md와의 차이

`CLAUDE.md`는 길이와 무관하게 **전체가 로드된다.** 200줄 제한은 자동 메모리 전용이다.
다만 `CLAUDE.md`도 200줄 이내로 유지하는 편이 지시사항 준수율에 유리하다.

## 활성화 / 비활성화

기본값은 **활성화**다. 끄는 방법은 두 가지이며, `/memory` 명령어의 토글로도 전환할 수 있다.

```bash
# 방법 1 — 환경변수
export CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
```

```json
// 방법 2 — settings.json
{
  "autoMemoryEnabled": false
}
```

다시 켜려면 환경변수를 제거하거나 `autoMemoryEnabled`를 `true`로 둔다.

## 이 저장소의 현재 상태 (2026-07-29 확인)

- `CLAUDE_CODE_DISABLE_AUTO_MEMORY` 미설정, `.claude/settings.local.json`에도
  `autoMemoryEnabled` 키 없음 (이 저장소에는 `.claude/settings.json` 자체가 없다)
  → 자동 메모리 **활성화** 상태다.
- 실제로 하네스가 자동 로드하는 `MEMORY.md`는 이 저장소 안이 아니라
  `~/.claude/projects/-Users-ryujun-Documents-cloud-whoareryu/memory/`에 있다.
  이 폴더(`.claude/memory/`)는 저장소에 커밋된 별도의 참고 문서 모음이며,
  세션 시작 시 하네스가 자동으로 읽는 경로가 아니다.
- 실제 자동 메모리의 `MEMORY.md`는 6줄로 200줄 한도에 여유가 많다.

## 이 규칙에서 따라오는 작성 원칙

- `MEMORY.md`는 **인덱스로만** 쓴다. 항목당 한 줄(제목 + 링크 + 짧은 훅)을 넘기지 않는다.
  내용을 여기에 적으면 매 세션 토큰을 먹으면서 200줄 한도를 잠식한다.
- 실제 내용은 주제 파일에 둔다. 주제 파일은 길어져도 자동 로드되지 않으므로 부담이 적다.
- 인덱스의 훅은 "이 파일을 열어야 할지" 판단할 수 있게 쓴다. 열어봐야 아는 문구는 쓸모없다.
- 항목이 200줄에 근접하면 오래되거나 틀린 메모리를 지운다. 줄 수를 줄이려고 훅을 지우지 않는다.

관련: [[docs-update-verify-against-repo]]