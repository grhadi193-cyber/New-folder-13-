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
      { protocol: 'https', hostname: '127.0.0.1' },
      { protocol: 'https', hostname: 'atifarzam.ir' },
	  { protocol: 'https', hostname: '192.168.1.4' }
    ],
  },
}
export default nextConfig
