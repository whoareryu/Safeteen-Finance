---
id: cloud.whoareryu
name: 새싹 (Saessak)
scope: www/ (Next.js 프론트엔드)
source: project-authored — 외부 레퍼런스 스크래핑이 아니라 이 저장소의 실제 코드
  (app/globals.css, components.json, app/layout.tsx, components/**)를 근거로 직접 작성했다.
verified: "2026-08-04"
omd: "0.1"
---

# Design System — cloud.whoareryu (www)

이 문서는 `www/` 프론트엔드의 실제 디자인 상태를 기록한 하네스 문서다. 외부
브랜드를 참고해 새로 만든 시스템이 아니라, **이미 손으로 다듬어진 기존 디자인을
있는 그대로 문서화**한 것이다 (`www/_docs/shadcn-rules.md`의 "기존 디자인 그대로
보존" 방침과 일치). 새 UI 작업은 이 문서를 어기지 않는 선에서 shadcn/ui
컴포넌트를 우선 사용한다.

## 1. Visual Theme & Atmosphere

이 사이트는 **의도적으로 분리된 3개의 비주얼 컨텍스트**를 동시에 쓴다. 하나로
통일하지 않는다 — 각각 다른 목적(제품 홈, 반려식물 앱, 강의 포트폴리오 아카이브)
을 가진다.

1. **Apple 스타일 헤더/홈** (`header.tsx`, `/` 홈 히어로) — 반투명 블러 헤더
   (`backdrop-filter: saturate(180%) blur(20px)`), 하드코딩된 뉴트럴/블루
   (`#1d1d1f`, `#0071e3`), 큰 여백의 마케팅형 레이아웃.
2. **새싹(Saessak) 테마** (`/plant/**`, `/admin/**`, `/mypage` 등, 기본값) —
   세이지 그린 액센트 + 따뜻한 종이톤 배경. shadcn CSS 변수(oklch) 기반.
3. **`.lesson-theme`** (`/portfolio/**`) — Netflix 레드 액센트. **새싹
   리브랜딩 대상이 아니다** — 하이미디어 아카데미 수강 과정 아카이브라는 별개
   맥락이라 의도적으로 보존한다.

## 2. Color Palette & Roles

모두 `app/globals.css`의 CSS 커스텀 프로퍼티(oklch)로 정의되고,
`components.json`(`cssVariables: true`, `baseColor: neutral`)을 통해 shadcn
컴포넌트가 그대로 상속한다. 값을 하드코딩하지 않고 시맨틱 토큰
(`bg-primary`, `text-foreground`, `border-border` 등)을 쓴다.

### 새싹(기본) — light
| 토큰 | 값 | 역할 |
|---|---|---|
| `--background` | `oklch(0.975 0.01 120)` | 따뜻한 종이톤 배경 |
| `--foreground` | `oklch(0.22 0.02 150)` | 본문 텍스트 |
| `--primary` | `oklch(0.58 0.13 145)` | 세이지 그린 액센트 (CTA, 활성 탭) |
| `--card` | `oklch(0.99 0.006 120)` | 카드 표면 |
| `--border` | `oklch(0.87 0.025 135)` | 테두리 |
| `--destructive` | `oklch(0.55 0.2 27)` | 경고/삭제 |

### 새싹 — dark
`--background: oklch(0.1 0.012 150)`, `--primary: oklch(0.68 0.15 145)` 등 —
`.dark` 클래스 아래 전체 세트가 별도 정의돼 있다 (`globals.css` 47–79행).

### `.lesson-theme` (Netflix 레드, `/portfolio` 전용)
| 토큰 | 값 |
|---|---|
| `--background` | `oklch(0.965 0.012 95)` (dark: `oklch(0.09 0 0)`) |
| `--primary` | `oklch(0.55 0.21 27)` (dark: `oklch(0.62 0.22 27)`) |

`/portfolio/**` 안에서 shadcn 컴포넌트를 쓸 때도 컴포넌트 자체에 색을
하드코딩하지 않는다 — `.lesson-theme`가 걸린 레이아웃 안에서 렌더되는 한 토큰이
자동으로 레드 팔레트로 바뀐다.

### Apple 헤더 전용 (하드코딩, 의도적 예외)
`.apple-nav-cta`, `.apple-cta-primary` 등은 시맨틱 토큰을 쓰지 않고
`#1d1d1f`/`#0071e3`/`#fbfbfd`를 직접 쓴다 — 애플 스타일을 정확히 재현하려는
의도적 선택이라, 다른 곳처럼 토큰화하지 않는다 (`globals.css` 302–376행).

## 3. Typography Rules

- **Sans**: Geist (`next/font/google` → `--font-sans: 'Geist', 'Geist Fallback'`)
- **Mono**: Geist Mono (`--font-mono`)
- 별도로 측정된 디스플레이 스케일 문서는 없다 — 실제 코드에서 반복 관찰되는
  크기만 정리:

| 역할 | 클래스 | 비고 |
|---|---|---|
| 페이지 타이틀 | `text-2xl sm:text-3xl font-semibold` | 히어로 헤딩 |
| 섹션 타이틀 | `text-xl font-bold` | |
| 본문 | `text-sm` | 대부분의 UI 텍스트 |
| 캡션/보조 | `text-xs text-muted-foreground` | 헤더 유저명, 타임스탬프 등 |

## 4. Component Stylings

`components.json`: `style: "new-york"`, `baseColor: "neutral"`,
`iconLibrary: "lucide"`, `rsc: true`. `components/ui/`에 거의 전체 shadcn
세트가 이미 설치돼 있다 (`npx shadcn@latest add`로 추가, 수동 편집 금지 —
`www/_docs/shadcn-rules.md` 참고).

기존 손터치 컴포넌트를 shadcn 프리미티브로 옮길 때 쓰는 패턴:
- **완전히 커스텀 스타일된 버튼** → `<Button variant="ghost" className="{기존 클래스 그대로}">`. `ghost`는 자체 배경색이 없어 기존 배경/테두리와 안 싸운다. 단 `ghost`의 `hover:bg-accent`가 기존 hover 색과 충돌하면, 기존 hover 배경을 className에 명시해 twMerge가 덮어쓰게 한다.
- **아이콘 버튼(`<a>`/`<button>`)** → `<Button asChild variant="ghost" size="icon" className="...">`.
- **손으로 짠 모달(`role="dialog"` + 오버레이 div)** → `Dialog`/`DialogContent`/`DialogClose` (Radix 포커스 트랩·ESC·포털 확보). 기존 패널 클래스(`modal-panel` 등)는 `DialogContent`의 기본 padding/radius를 className으로 덮어써서 그대로 재현.
- **순수 페이지 네비게이션 링크(`<Link>`)** → 버튼처럼 안 생겼으면 강제로 `Button asChild`로 감싸지 않는다. `Tabs`도 페이지 라우팅에는 쓰지 않는다 (Radix Tabs는 콘텐츠 전환용이지 라우팅용이 아님).

## 5. Layout Principles

- 헤더는 `fixed` + `--site-header-height` CSS 변수로 본문 상단 패딩을 계산
  (`.site-main-below-header`). `/portfolio` 하위는 서브바가 추가돼
  `--site-header-height-lesson`으로 늘어난다.
- 모바일 하단 탭바(`BottomTabBar`)는 `/portfolio` 이하에서는 숨긴다.
- 콘텐츠 컨테이너 폭: 좁은 폼/채팅형은 `max-w-2xl`, 랜딩/그리드형은
  `max-w-6xl`.
- 모바일 하단 safe-area는 `pb-[max(0.75rem,env(safe-area-inset-bottom))]`
  패턴으로 처리.

## 6. Depth & Elevation

- 카드/표면: `border border-border` + `shadow-sm` (`.surface-white`,
  `.card-light`).
- 글래스 효과: 헤더(`backdrop-filter: blur(20px)`), 하단 탭바
  (`.saessak-glass-panel`) 둘 다 반투명 + 블러.
- 모달: `shadow-xl` (`.modal-panel`), 오버레이는 `bg-neutral-900/40
  backdrop-blur-sm`.

## 7. Do's and Don'ts

### Do
- 새 UI는 `components/ui/`의 shadcn 프리미티브를 우선 쓴다 (§4 패턴 참고).
- 색은 시맨틱 토큰(`bg-primary`, `text-foreground`, `border-border`)으로
  쓴다 — Apple 헤더 전용 하드코딩(§2)은 기존 코드에 한해 예외로 유지한다.
- `/portfolio/**`는 `.lesson-theme`(레드) 그대로 유지한다.
- `components/ui/` 내부 파일은 직접 고치지 않는다 — CLI로 다시 add.

### Don't
- 3개 테마를 하나로 통일하려 하지 않는다 (의도된 분리다).
- shadcn 컴포넌트 도입한다고 기존 시각 디자인을 shadcn 기본 zinc/neutral
  룩으로 갈아엎지 않는다 — 구조만 옮기고 외관은 보존한다.
- `Dialog` 자리에 파괴적 확인(삭제 등)을 넣지 않는다 — `AlertDialog`를 쓴다
  (아직 이 저장소에 파괴적 확인 흐름은 없음 — 생기면 적용).
- 인라인 `style` 속성 금지 (`www/CLAUDE.md` 기존 규칙).

## 8. Responsive Behavior

- 헤더: 데스크톱은 가운데 "LESSON" 내비 + 오른쪽 액션 전부 노출, 모바일은
  가운데 내비를 숨기고 우측 스크롤 영역에 축소된 항목만 노출
  (`md:block`/`md:hidden` 분기).
- 날씨 위젯은 홈(`/`)에서만, 그리고 `sm:` 이상에서만 노출.
- 하단 탭바는 모바일 전용 내비게이션이며 데스크톱에서도 항상 보이지만
  실질적으로 모바일 사용을 전제로 설계됨 (safe-area 대응 포함).

## 9. Agent Prompt Guide

- "새싹 테마에 맞는 카드 하나 추가해줘" → `Card`/`CardContent` +
  `bg-card text-card-foreground border-border` (시맨틱 토큰만, §2 참고).
- "/portfolio 안에 강의 카드 추가해줘" → 같은 `Card` 컴포넌트를 쓰되 별도
  색 지정 없이 `.lesson-theme` 컨텍스트 안에서 렌더 — 자동으로 레드 팔레트.
- "헤더에 버튼 하나 추가해줘" → §4의 "완전히 커스텀 스타일된 버튼" 패턴
  (`Button variant="ghost"` + 기존 클래스 유지) 따라간다.
- "모달 하나 새로 만들어줘" → 손으로 `role=dialog` div 짜지 말고 `Dialog`
  컴포넌트로 시작한다.

## 10. Voice & Tone

한국어, 반말이 아닌 존댓말이지만 친근한 어미("~해요", "~드려요",
"~볼까요"). 새싹이(AI 어시스턴트 캐릭터)는 "새싹이에게 물어보기"처럼
1인칭 캐릭터로 등장한다. 에러 메시지도 딱딱한 시스템 톤이 아니라 사용자에게
직접 말하듯 쓴다 (`.claude/rules/api-standards.md`: `HTTPException` `detail`도
한국어 자연문으로). 과장된 영업 카피는 쓰지 않는다 — "잎사귀 사진 한 장이면
품종과 병징을 바로 알려드려요"처럼 기능을 담백하게 설명하는 톤.

## 11. Brand Narrative

**새싹**은 AI 반려식물 케어 에이전트다 — 잎사귀 사진으로 품종·병징을
진단하고, 날씨 기반 물주기 알림과 케어 일정을 챙겨주는 게 핵심 가치. 홈
화면의 Apple 스타일 마케팅 톤은 "제품처럼 보이는 진입점"을 의도한 것이고,
실제 기능 화면(진단/마이플랜트/케어일정)은 새싹 세이지그린 테마로 넘어간다.

`/portfolio`는 별개 맥락이다 — 하이미디어 아카데미 재직자 과정에서 진행한
프로젝트(타이타닉 분석, Vision, LangChain 챗 등)를 모아둔 **강의 포트폴리오
아카이브**이며, 새싹 제품과는 다른 청중(과정 리뷰어)을 대상으로 한다. 그래서
새싹 리브랜딩 때도 이 영역은 의도적으로 손대지 않았다.

## 12. Principles

1. 3개 테마 각자의 존재 이유를 존중한다 — 통일은 목표가 아니다.
2. shadcn은 구조(접근성, 상태 관리, 포커스 트랩)를 얻기 위해 쓰지, 외관을
   갈아엎기 위해 쓰지 않는다.
3. 새 시크릿/색상은 항상 시맨틱 토큰으로 — Apple 헤더의 하드코딩은 예외지,
   새 규범이 아니다.
4. 사용자에게 보이는 텍스트(에러 포함)는 한국어, 담백하고 직접적으로.

## 13. Personas

- **반려식물 초보자** (새싹 메인 사용자): 식물 이름도 잘 모르는 상태에서
  사진 한 장으로 답을 얻고 싶어 함 — 진단 흐름은 최대한 짧아야 함.
- **과정 수강생/리뷰어** (`/portfolio` 방문자): 프로젝트 결과물을 훑어보러
  옴 — 새싹 브랜딩보다 프로젝트 내용 자체가 중요, 레드 테마는 그대로 둬도
  무방.

## 14. States

로딩/에러/빈 상태 처리는 아직 페이지마다 제각각이고, 공통 컴포넌트로 묶여
있지 않다 (`www/CLAUDE.md` 알려진 이슈: "공통 에러 바운더리·로딩 UI 미구현").
새 화면을 만들 때 `Skeleton`/`Alert`/`Empty`(이미 `components/ui/`에 있음)를
우선 쓰고, 기존 화면을 고칠 일이 있으면 그때 정리한다 — 지금 이 문서 작성
시점에 일괄 정리하지는 않았다.

## 15. Motion & Easing

별도로 정의된 easing 토큰은 없다. `transition-all`/`transition-colors`
+ Tailwind 기본 duration을 그대로 쓴다 (`tw-animate-css`가 devDependency로
들어있어 필요하면 `animate-in`/`animate-out` 유틸을 shadcn Dialog 등에서
이미 쓰고 있음 — `components/ui/dialog.tsx` 참고).

---

**작성 근거:** `app/globals.css`, `components.json`, `app/layout.tsx`,
`components/header.tsx`, `components/footer.tsx`, `components/auth-modal.tsx`,
`components/bottom-tab-bar.tsx` 등 이 저장소의 실제 코드. 외부 사이트
스크래핑이나 레퍼런스 카탈로그를 참고하지 않았다.
**범위:** `www/`(Next.js 프론트엔드)만 다룬다. `fastapi`/`flutter`는 별도
UI 시스템(Flutter 위젯 기반)이라 이 문서의 대상이 아니다.
