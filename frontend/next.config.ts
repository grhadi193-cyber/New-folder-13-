import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: path.join(__dirname),
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: 'http', hostname: 'localhost', port: '8000' },
      { protocol: 'http', hostname: '127.0.0.1', port: '8000' },
      { protocol: 'http', hostname: 'backend', port: '8000' },
      { protocol: 'https', hostname: 'farzamback-farazmgps.runflare.run' },
      { protocol: 'https', hostname: 'farazmgps.runflare.run' },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://farzamback-farazmgps.runflare.run/api/:path*',
      },
      {
        source: '/public/media/:path*',
        destination: 'https://farzamback-farazmgps.runflare.run/public/media/:path*',
      },
    ]
  },
}
export default nextConfig
