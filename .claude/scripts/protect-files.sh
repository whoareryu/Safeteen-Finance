#!/bin/bash
# stdin에서 JSON 입력을 읽음
INPUT=$(cat)

# 수정하려는 파일 경로 추출
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.path // .tool_input.file_path // ""')

# 보호할 파일 — 이 저장소의 실제 시크릿 파일들
# (.env*: fastapi/.env, fastapi/.env.auth, www/.env.local, 루트 .env 등
#  *.pem: JWT_PRIVATE_KEY 등 RS256 키 — auth-gateway 분리 참고)
# 단, *.env.example / *.env.*.example 같은 템플릿 파일은 시크릿이 아니므로 제외한다
# (실제 값 없이 커밋되는 예시 파일 — CLAUDE.md 규칙상 오히려 갱신 대상).
BASENAME=$(basename -- "$FILE_PATH")

if [[ "$BASENAME" == .env* && "$BASENAME" != *.example ]]; then
  echo "보안 정책: $FILE_PATH 파일은 수정할 수 없습니다." >&2
  exit 2
fi

if [[ "$BASENAME" == *.pem || "$BASENAME" == *.key || "$BASENAME" == secrets.* ]]; then
  echo "보안 정책: $FILE_PATH 파일은 수정할 수 없습니다." >&2
  exit 2
fi

exit 0
