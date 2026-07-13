import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { GoogleOAuthProvider } from '@react-oauth/google'
import Header from '@/components/header'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthProvider } from '@/components/auth-provider'
import FloatingChat from '@/components/floating-chat'
import BottomTabBar from '@/components/bottom-tab-bar'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: '방구석 플랜트 매니저 | AI 반려식물 케어 가이드',
  description:
    '잎사귀 사진 한 장으로 품종과 상태를 진단하고, 날씨에 맞춘 물주기 알림과 케어 처방을 받는 반려식물 케어 에이전트',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="bg-background" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? ""}>
          <AuthProvider>
            <Header />
            <div className="site-main-below-header relative z-10 min-h-screen bg-transparent">
              {children}
            </div>
            <FloatingChat />
            <BottomTabBar />
            {process.env.NODE_ENV === 'production' && <Analytics />}
          </AuthProvider>
          </GoogleOAuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
