#!/bin/bash

PROJECT_ID="jb-silver-connect"
SUBSCRIPTION="gmail-push-sub"
WEBHOOK_PATH="/webhook/6cb631de-6505-47c3-a978-e0d628a56e64"

echo "[tunnel] cloudflared 시작 중..."

cloudflared tunnel --url http://localhost:5678 2>&1 | while IFS= read -r line; do
  echo "$line"
  if [[ "$line" == *"trycloudflare.com"* ]] && [[ -z "$URL_UPDATED" ]]; then
    URL=$(echo "$line" | grep -o 'https://[a-zA-Z0-9\-]*\.trycloudflare\.com')
    if [[ -n "$URL" ]]; then
      ENDPOINT="${URL}${WEBHOOK_PATH}"
      echo "[tunnel] URL 감지: $URL"
      echo "[tunnel] Pub/Sub 엔드포인트 업데이트 중..."
      gcloud pubsub subscriptions modify-push-config "$SUBSCRIPTION" \
        --push-endpoint="$ENDPOINT" \
        --project="$PROJECT_ID"
      echo "[tunnel] 완료: $ENDPOINT"
      export URL_UPDATED=1
    fi
  fi
done
