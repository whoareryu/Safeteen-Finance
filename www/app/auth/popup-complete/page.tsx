"use client";

import { useEffect } from "react";
import { WR_AUTH_COMPLETE_MESSAGE } from "@/lib/auth";

export default function PopupCompletePage() {
  useEffect(() => {
    if (window.opener) {
      window.opener.postMessage({ type: WR_AUTH_COMPLETE_MESSAGE }, window.location.origin);
      window.close();
    } else {
      // 팝업이 아니라 직접 접근한 경우(북마크, 팝업 차단 등) — 홈으로 보낸다.
      window.location.href = "/";
    }
  }, []);

  return (
    <div className="flex min-h-[50vh] items-center justify-center p-4 text-center text-sm text-muted-foreground">
      로그인이 완료되었습니다. 이 창은 자동으로 닫힙니다.
    </div>
  );
}
