/** @type {import('next').NextConfig} */
const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";

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
  async redirects() {
    return [
      { source: "/history", destination: "/", permanent: true },
      { source: "/nature", destination: "/food/hansik", permanent: true },
      { source: "/notice", destination: "/", permanent: true },
      { source: "/restaurant", destination: "/food/hansik", permanent: true },
      { source: "/shopping", destination: "/", permanent: true },
      { source: "/attraction", destination: "/", permanent: true },
      { source: "/seoulmate", destination: "/portfolio", permanent: true },
      { source: "/portfolio/seoulmate", destination: "/portfolio", permanent: true },
      { source: "/titanic", destination: "/portfolio/titanic", permanent: true },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api/chat",
        destination: `${backendUrl}/chat`,
      },
      {
        source: "/api/titanic/chat",
        destination: `${backendUrl}/titanic/chat`,
      },
      {
        source: "/api/titanic/upload",
        destination: `${backendUrl}/titanic/upload`,
      },
      {
        source: "/api/signup",
        destination: `${backendUrl}/signup`,
      },
      {
        source: "/api/login",
        destination: `${backendUrl}/login`,
      },
      {
        source: "/api/auth/:path*",
        destination: `${backendUrl}/auth/:path*`,
      },
      {
        source: "/api/gourmet/:path*",
        destination: `${backendUrl}/gourmet/:path*`,
      },
    ];
  },
};

export default nextConfig;
