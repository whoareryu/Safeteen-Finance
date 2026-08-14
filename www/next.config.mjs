/** @type {import('next').NextConfig} */
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.whoareryu.cloud";
// auth-gateway-harness: 로그인/세션 관련 경로는 별도 auth 서비스(auth.whoareryu.cloud)로 분리됐다.
const authUrl = process.env.NEXT_PUBLIC_AUTH_URL || "https://auth.whoareryu.cloud";

const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
        pathname: "/**",
      },
    ],
  },
  async headers() {
    return [
      {
        source: "/_next/:path*",
        headers: [{ key: "Cache-Control", value: "no-store, must-revalidate" }],
      },
    ];
  },
  async redirects() {
    return [
      { source: "/history", destination: "/", permanent: true },
      { source: "/notice", destination: "/", permanent: true },
      { source: "/shopping", destination: "/", permanent: true },
      { source: "/attraction", destination: "/", permanent: true },
      { source: "/seoulmate", destination: "/", permanent: true },
      { source: "/portfolio", destination: "/", permanent: true },
      { source: "/portfolio/:path*", destination: "/", permanent: true },
      { source: "/titanic", destination: "/", permanent: true },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api/chat",
        destination: `${backendUrl}/chat`,
      },
      {
        // owner-check는 owner_session.py 기반이라 RS256 auth 서비스로 옮기지 않고
        // 백엔드에 남겨뒀다 — 더 구체적인 규칙이라 아래 catch-all보다 먼저 와야 한다.
        source: "/api/auth/owner-check",
        destination: `${backendUrl}/auth/owner-check`,
      },
      {
        source: "/api/auth/:path*",
        destination: `${authUrl}/auth/:path*`,
      },
      {
        source: "/api/safeteen/:path*",
        destination: `${backendUrl}/api/safeteen/:path*`,
      },
    ];
  },
};

export default nextConfig;
