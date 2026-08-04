# shadcn/ui 사용 규칙

상위 규칙은 [[www/CLAUDE\|www/CLAUDE]]를 먼저 읽는다. 색상·타이포·컴포넌트
스타일링의 상세 근거는 `www/DESIGN.md`를 참고한다.

---

## 원칙

`components/ui/`에 이미 shadcn/ui 컴포넌트 세트(`components.json` — style: `new-york`,
baseColor: `neutral`, iconLibrary: `lucide`)가 설치돼 있다. **새 UI를 만들 때는 raw
`<div>`/`<button>`/`<input>` 등으로 직접 짜지 않고, 대응하는 shadcn 컴포넌트가
있으면 그걸 우선 쓴다.**

| 원하는 것 | 쓸 것 |
|-----------|-------|
| 버튼 | `components/ui/button.tsx` (`Button`) |
| 카드형 컨테이너 | `components/ui/card.tsx` (`Card`) |
| 모달·확인창 | `components/ui/dialog.tsx` / 파괴적 확인은 `alert-dialog.tsx` |
| 폼 입력 | `components/ui/input.tsx`, `label.tsx`, `form.tsx` (+ react-hook-form/zod) |
| 표 | `components/ui/table.tsx` |
| 탭 전환 | `components/ui/tabs.tsx` |
| 뱃지·상태 표시 | `components/ui/badge.tsx` |
| 드롭다운·컨텍스트 메뉴 | `components/ui/dropdown-menu.tsx` |

`components/ui/`에 필요한 컴포넌트가 없으면 직접 새로 만들지 말고
`npx shadcn@latest add <컴포넌트명>`으로 추가한다. **`components/ui/` 내부 파일은
자동생성물이라 손으로 고치지 않는다** (필요하면 CLI로 다시 add하거나, 정말
커스터마이징이 필요할 때만 예외적으로 수정하고 이유를 주석으로 남긴다).

---

## 테마 — 두 개의 디자인 컨텍스트

`app/globals.css`에 CSS 변수(`--background`, `--primary`, `--border` 등, oklch)로
정의된 테마가 두 개 있다. shadcn 컴포넌트는 이 변수들을 그대로 상속하므로,
색상을 하드코딩(`bg-green-600` 등)하지 않고 항상 `bg-primary`/`text-foreground`/
`border-border` 같은 시맨틱 토큰을 쓴다.

| 컨텍스트 | 적용 범위 | 특징 |
|----------|-----------|------|
| 기본(새싹) | `/`, `/plant/**`, `/admin/**`, `/mypage` 등 | 세이지 그린 액센트, 따뜻한 종이톤 배경 |
| `.lesson-theme` | `/portfolio/**` | Netflix 레드 테마 — **새싹 리브랜딩 대상 아님, 임의로 색 바꾸지 않는다** |

`/portfolio/**` 하위를 shadcn 컴포넌트로 옮길 때도 `lesson-theme` 클래스가 걸린
루트(레이아웃) 안에서 렌더되는 한 색은 자동으로 맞춰진다 — 컴포넌트 자체에 별도
색상 오버라이드를 넣지 않는다.

---

## 마이그레이션 상태

2026-08-04 기준 `app/` 페이지 대부분이 아직 raw HTML + 커스텀 클래스(`saessak-*`
등)로 되어 있고, shadcn 컴포넌트를 쓰는 페이지는 소수다. 기존 페이지를 건드릴
일이 있으면(버그 수정이든 기능 추가든) 그 참에 해당 페이지의 관련 마크업을
shadcn 컴포넌트로 옮긴다 — 전체를 한 번에 다 바꾸는 대규모 리라이트가 진행
중이며, 그 과정에 못 미친 페이지는 다음에 손댈 때 정리한다.
