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
        destination: `${backendUrl}/api/titanic/chat`,
      },
      {
        source: "/api/titanic/upload",
        destination: `${backendUrl}/api/titanic/upload`,
      },
      {
        source: "/api/titanic/james/upload",
        destination: `${backendUrl}/api/titanic/james/upload`,
      },
      {
        source: "/api/titanic/walter/myself",
        destination: `${backendUrl}/api/titanic/walter/myself`,
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
      {
        source: "/api/weather/icon",
        destination: `${backendUrl}/weather/icon`,
      },
      {
        source: "/api/weather",
        destination: `${backendUrl}/weather`,
      },
      {
        source: "/api/silicon-valley/:path*",
        destination: `${backendUrl}/api/silicon-valley/:path*`,
      },
      {
        source: "/api/chef/:path*",
        destination: `${backendUrl}/api/chef/:path*`,
      },
      {
        source: "/api/ontology/:path*",
        destination: `${backendUrl}/api/ontology/:path*`,
      },
    ];
  },
};

export default nextConfig;
