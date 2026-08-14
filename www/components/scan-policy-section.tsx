import { ExternalLink, Landmark } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AlternativePolicy } from "@/lib/safeteen-api";

// TODO: 실제 연동 시 lib/safeteen-api.ts의 listPolicies()로 교체 — 지금은 UI 스켈레톤용 mock 데이터.
const MOCK_POLICIES: (AlternativePolicy & { rateBadge: string })[] = [
  {
    title: "햇살론 유스",
    description: "만 34세 이하 사회초년생·대학(원)생을 위한 저금리 정책 서민금융상품.",
    official_link: "https://www.kinfa.or.kr",
    rateBadge: "연 3.6% · 최대 1,200만원",
  },
  {
    title: "청년 긴급생계비 지원",
    description: "실직·휴폐업 등으로 생계가 어려운 청년에게 소액 생계비를 무이자로 지원.",
    official_link: "https://www.kinfa.or.kr",
    rateBadge: "무이자 · 최대 100만원",
  },
  {
    title: "청년 미소금융",
    description: "저신용·저소득 청년의 창업·생계자금을 지원하는 미소금융중앙재단 상품.",
    official_link: "https://www.smilemicrocredit.or.kr",
    rateBadge: "연 4.5% 이하",
  },
];

export default function PolicySection() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900 sm:text-2xl">
          돈이 급할 때 이용할 수 있는 안전한 청년 금융 정책
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          불법 대출 대신, 정부·공공기관이 보증하는 합법 지원 제도를 먼저 확인하세요.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {MOCK_POLICIES.map((policy) => (
          <Card key={policy.title} className="flex flex-col border-slate-200 shadow-sm">
            <CardHeader>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
                <Landmark className="h-5 w-5" aria-hidden />
              </div>
              <CardTitle className="text-base">{policy.title}</CardTitle>
              <Badge variant="outline" className="w-fit rounded-full border-indigo-200 bg-indigo-50 text-indigo-700">
                {policy.rateBadge}
              </Badge>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col justify-between gap-4">
              <CardDescription className="text-sm leading-relaxed">{policy.description}</CardDescription>
              <a
                href={policy.official_link}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
              >
                공식 홈페이지 신청하기
                <ExternalLink className="h-3.5 w-3.5" aria-hidden />
              </a>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
