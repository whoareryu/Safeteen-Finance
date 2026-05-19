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
  async rewrites() {
    return [
      {
        source: "/api/chat",
        destination: `${backendUrl}/chat`,
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
