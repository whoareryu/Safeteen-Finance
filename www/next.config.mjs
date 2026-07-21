/** @type {import('next').NextConfig} */
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.whoareryu.cloud";

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
        source: "/api/auth/:path*",
        destination: `${backendUrl}/auth/:path*`,
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
      {
        source: "/api/vision/:path*",
        destination: `${backendUrl}/api/vision/:path*`,
      },
      {
        source: "/api/plant/:path*",
        destination: `${backendUrl}/api/plant/:path*`,
      },
    ];
  },
};

export default nextConfig;
