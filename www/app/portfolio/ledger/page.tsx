import { Card, CardContent, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const FEATURES = [
  {
    title: "지출 항목 기록",
    description: "날짜·카테고리·금액·메모로 하루하루의 지출을 빠르게 기록합니다.",
  },
  {
    title: "카테고리별 통계",
    description: "식비·교통·주거 등 카테고리별 지출 비중을 월 단위로 시각화합니다.",
  },
  {
    title: "예산 알림",
    description: "카테고리별 월 예산을 설정하고 초과 시 알림을 받습니다.",
  },
];

const STACK = ["Next.js", "TypeScript", "FastAPI", "PostgreSQL"];

export default function LedgerPage() {
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
          매일의 수입·지출을 기록하고 카테고리별 지출 흐름을 한눈에 보여주는 가계부 웹
          애플리케이션입니다.
        </p>
      </section>

      <section className="mx-auto max-w-3xl px-6 py-12 md:py-16">
        <div className="flex flex-wrap gap-2">
          {STACK.map((s) => (
            <Badge key={s} variant="secondary">
              {s}
            </Badge>
          ))}
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {FEATURES.map((f) => (
            <Card key={f.title}>
              <CardContent>
                <CardTitle className="text-base">{f.title}</CardTitle>
                <CardDescription className="mt-1.5">{f.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        <p className="mt-8 text-sm text-muted-foreground">
          하이미디어 재직자 과정에서 진행 예정인 프로젝트입니다. 진행되면 이 페이지에 실제
          데모와 상세 내용이 채워집니다.
        </p>
      </section>
    </div>
  );
}
