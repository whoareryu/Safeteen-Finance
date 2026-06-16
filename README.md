# v0-developer-branding-page

This is a [Next.js](https://nextjs.org) project bootstrapped with [v0](https://v0.app).

## Built with v0

This repository is linked to a [v0](https://v0.app) project. You can continue developing by visiting the link below -- start new chats to make changes, and v0 will push commits directly to this repo. Every merge to `main` will automatically deploy.

[Continue working on v0 →](https://v0.app/chat/projects/prj_SLLKGDgdqPt701zP0ucxL1BPGVhE)

### Vercel에서 "Deployment was blocked" 가 나올 때

빌드 오류가 아니라 **커밋 작성자 ↔ Vercel/GitHub 연동** 문제인 경우가 많습니다.

1. [Vercel → Authentication](https://vercel.com/account/settings/authentication) 에서 **GitHub 재연결**
2. `git config user.email` 이 GitHub·Vercel과 동일한지 확인
3. [Hobby 플랜](https://vercel.com/docs/plans/hobby) 은 **본인 커밋**만 자동 배포 — v0/타 계정 커밋이면 본인으로 **새 커밋** push
4. Vercel **Environment Variables** 에 `BACKEND_URL` = 공개 백엔드 URL ( `127.0.0.1` 불가 )

상세: 모노레포 저장소 `com.ragwatson` 의 `docs/DevOps/Frontend/VERCEL_V0_DEPLOY.md`

---

## 관련 문서

[[www/CLAUDE\|Frontend CLAUDE]]

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

## Learn More

To learn more, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [v0 Documentation](https://v0.app/docs) - learn about v0 and how to use it.

<a href="https://v0.app/chat/api/kiro/clone/whoareryu/v0-developer-branding-page" alt="Open in Kiro"><img src="https://pdgvvgmkdvyeydso.public.blob.vercel-storage.com/open%20in%20kiro.svg?sanitize=true" /></a>
