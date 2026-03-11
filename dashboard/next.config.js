/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8420/api/:path*",
      },
      {
        source: "/auth/:path*",
        destination: "http://localhost:8420/auth/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
