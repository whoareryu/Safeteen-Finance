"use client";

import { useState } from "react";
import { AlertTriangle, Check, Copy, Phone, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { EmergencyGuide } from "@/lib/safeteen-api";

// TODO: 실제 연동 시 lib/safeteen-api.ts의 fetchEmergencyGuide()로 교체 — 지금은 UI 스켈레톤용 mock 데이터.
const MOCK_GUIDE: EmergencyGuide = {
  account_freeze_steps: [
    { order: 1, title: "지급정지 신청", description: "피해 계좌로 입금한 금융회사 콜센터(또는 앱)에 즉시 전화해 지급정지를 신청한다." },
    { order: 2, title: "피해 사실 신고", description: "112 또는 사이버범죄 신고시스템(ECRM)에 신고하고 사건사고사실확인원을 발급받는다." },
    { order: 3, title: "확인원 제출", description: "발급받은 사건사고사실확인원을 계좌 개설 금융회사에 제출해 지급정지를 연장·확정한다." },
  ],
  police_report_steps: [
    { order: 1, title: "112 또는 사이버수사대 신고", description: "가까운 경찰서 방문 또는 112, 사이버범죄 신고시스템(ECRM)으로 신고한다." },
    { order: 2, title: "증거자료 확보", description: "대화 캡처, 계좌번호, 통화 녹음, 송금 내역 등 관련 증거를 미리 정리해 둔다." },
    { order: 3, title: "고소장·진술 접수", description: "경찰서 방문 또는 온라인으로 고소장을 접수하고 담당 수사관 배정을 확인한다." },
  ],
  hotlines: [
    { name: "경찰청 사이버수사국", phone_number: "182", description: "사이버 사기·금융범죄 신고" },
    { name: "금융감독원", phone_number: "1332", description: "불법 사금융·보이스피싱 상담" },
    { name: "청소년 사이버 상담센터", phone_number: "1388", description: "청소년 대상 피해 상담" },
  ],
};

const INCIDENT_TEMPLATE = `[사건 경위서]
1. 발생 일시:
2. 접촉 경로(SNS/메신저):
3. 상대방 정보(계좌번호, 연락처, 아이디):
4. 피해 경위(요구받은 내용, 송금 내역):
5. 보유 증거(캡처, 통화 녹음 등):`;

export default function EmergencyGuideSection() {
  const guide = MOCK_GUIDE;
  const [copied, setCopied] = useState(false);

  async function copyTemplate() {
    await navigator.clipboard.writeText(INCIDENT_TEMPLATE);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-rose-600" aria-hidden />
        <div>
          <p className="text-sm font-semibold text-rose-800">이미 금융사기에 휘말리셨나요?</p>
          <p className="mt-1 text-sm text-rose-700">당황하지 마세요. 아래 순서대로 지금 바로 조치하면 피해를 줄일 수 있습니다.</p>
        </div>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ShieldAlert className="h-4 w-4 text-indigo-600" aria-hidden />
            Step 1. 즉시 계좌 지급정지 신청
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {guide.account_freeze_steps.map((step) => (
            <div key={step.order} className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700">
                {step.order}
              </span>
              <div>
                <p className="text-sm font-medium text-slate-800">{step.title}</p>
                <p className="text-sm text-slate-500">{step.description}</p>
              </div>
            </div>
          ))}
          <a
            href="tel:1332"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700"
          >
            <Phone className="h-4 w-4" aria-hidden />
            금융감독원 1332 바로 연결
          </a>
        </CardContent>
      </Card>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ShieldAlert className="h-4 w-4 text-indigo-600" aria-hidden />
            Step 2. 경찰 신고 및 증거 수집
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {guide.police_report_steps.map((step) => (
            <div key={step.order} className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700">
                {step.order}
              </span>
              <div>
                <p className="text-sm font-medium text-slate-800">{step.title}</p>
                <p className="text-sm text-slate-500">{step.description}</p>
              </div>
            </div>
          ))}
          <Button
            type="button"
            variant="outline"
            onClick={copyTemplate}
            className="border-slate-200 text-slate-700 hover:bg-slate-100"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-600" /> : <Copy className="h-4 w-4" />}
            {copied ? "복사됨" : "AI 사건 경위서 템플릿 복사하기"}
          </Button>
        </CardContent>
      </Card>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">긴급 연락처</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-3">
          {guide.hotlines.map((hotline) => (
            <a
              key={hotline.name}
              href={`tel:${hotline.phone_number}`}
              className="flex flex-col gap-1 rounded-lg border border-slate-200 p-3 transition hover:border-indigo-300 hover:bg-indigo-50"
            >
              <span className="text-lg font-bold tabular-nums text-indigo-600">{hotline.phone_number}</span>
              <span className="text-sm font-medium text-slate-800">{hotline.name}</span>
              <span className="text-xs text-slate-500">{hotline.description}</span>
            </a>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
