"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { listReceipts, type Receipt } from "@/lib/ledger-api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

function formatWon(amount: number): string {
  return `${Math.round(amount).toLocaleString("ko-KR")}원`;
}

export default function LedgerPage() {
  const { user, ready } = useAuth();
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready || !user) return;
    let cancelled = false;
    setLoading(true);
    listReceipts()
      .then((data) => {
        if (!cancelled) setReceipts(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "영수증 목록을 불러오지 못했습니다.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ready, user]);

  const totalThisMonth = receipts.reduce((sum, r) => sum + r.total_amount, 0);

  return (
    <div className="min-h-[calc(100dvh-var(--site-header-height))] bg-background">
      <section className="relative flex min-h-[36vh] flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-[#0c291f] via-[#1e5f3a] to-[#0a2818] px-6 py-14 text-center text-white md:py-16">
        <div
          className="pointer-events-none absolute inset-0 opacity-50"
          style={{
            background:
              "radial-gradient(ellipse 70% 45% at 50% 110%, rgba(52,211,153,0.35) 0%, transparent 50%)",
          }}
          aria-hidden
        />
        <p className="relative z-10 text-sm font-medium text-white/70">수업용</p>
        <h1 className="relative z-10 mt-2 text-4xl font-semibold md:text-5xl">가계부</h1>
        <p className="relative z-10 mt-4 max-w-lg text-base text-white/85 md:text-lg">
          앱에서 촬영한 영수증이 S3에 저장되고, Gemini Vision이 상호명·금액·품목을 읽어
          자동으로 기록합니다.
        </p>
      </section>

      <section className="mx-auto max-w-2xl px-6 py-12 md:py-16">
        {!ready ? null : !user ? (
          <div className="text-center">
            <p className="text-sm text-muted-foreground">로그인하면 내 영수증 목록을 볼 수 있어요.</p>
            <Button asChild variant="outline" className="mt-6">
              <Link href="/">홈으로</Link>
            </Button>
          </div>
        ) : (
          <>
            <Card className="mb-6">
              <CardContent className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">전체 지출</span>
                <span className="text-xl font-semibold text-foreground">
                  {formatWon(totalThisMonth)}
                </span>
              </CardContent>
            </Card>

            {loading ? (
              <p className="text-sm text-muted-foreground">불러오는 중…</p>
            ) : error ? (
              <p className="text-sm text-destructive">{error}</p>
            ) : receipts.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                아직 등록된 영수증이 없어요. 앱에서 영수증을 촬영해 올려보세요.
              </p>
            ) : (
              <Accordion type="single" collapsible className="space-y-3">
                {receipts.map((receipt) => (
                  <Card key={receipt.id} className="overflow-hidden p-0">
                    <AccordionItem value={String(receipt.id)} className="border-0">
                      <AccordionTrigger className="px-5 py-4 hover:no-underline">
                        <div className="flex flex-1 items-center justify-between gap-3 pr-2 text-left">
                          <div className="min-w-0">
                            <p className="truncate font-medium text-foreground">
                              {receipt.store_name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {receipt.purchase_date}
                            </p>
                          </div>
                          <div className="flex shrink-0 items-center gap-2">
                            <Badge variant="secondary">{receipt.category}</Badge>
                            <span className="font-semibold text-foreground">
                              {formatWon(receipt.total_amount)}
                            </span>
                          </div>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="px-5 pb-5">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={receipt.image_url}
                          alt={`${receipt.store_name} 영수증`}
                          className="mb-3 max-h-60 w-full rounded-lg border border-border object-contain"
                        />
                        {receipt.items.length > 0 ? (
                          <ul className="space-y-1.5 text-sm">
                            {receipt.items.map((item, idx) => (
                              <li key={idx} className="flex items-center justify-between gap-2">
                                <span className="text-foreground">
                                  {item.name}
                                  {item.quantity > 1 ? ` × ${item.quantity}` : ""}
                                </span>
                                <span className="text-muted-foreground">{formatWon(item.amount)}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-muted-foreground">품목 내역을 읽지 못했어요.</p>
                        )}
                      </AccordionContent>
                    </AccordionItem>
                  </Card>
                ))}
              </Accordion>
            )}
          </>
        )}
      </section>
    </div>
  );
}
