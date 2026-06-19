import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import Header from '@/components/header'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthProvider } from '@/components/auth-provider'
import { FavoritesProvider } from '@/components/favorites-provider'
import { NearbyLocationProvider } from '@/components/nearby-location-provider'
import { CategoryMenuProvider } from '@/components/category-menu-context'
import CategorySidebarDrawer from '@/components/category-sidebar-drawer'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'GourmetMate | 서울 맛집 AI 가이드',
  description:
    '서울 맛집을 AI로 카테고리별 검색·추천하고 메뉴·분위기 정보를 받아보는 GourmetMate',
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
          <AuthProvider>
            <FavoritesProvider>
            <NearbyLocationProvider>
            <CategoryMenuProvider>
              <CategorySidebarDrawer />
              <Header />
              <div className="site-main-below-header relative z-10 min-h-screen bg-transparent">
                {children}
              </div>
            </CategoryMenuProvider>
            {process.env.NODE_ENV === 'production' && <Analytics />}
            </NearbyLocationProvider>
            </FavoritesProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
