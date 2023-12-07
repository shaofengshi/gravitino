/*
 * Copyright 2023 Datastrato.
 * This software is licensed under the Apache License version 2.
 */

const isProdEnv = process.env.NODE_ENV === 'production'

const apiUrl = process.env.NEXT_PUBLIC_API_URL
const oauthUri = process.env.NEXT_PUBLIC_OAUTH_URI
const oauthPath = process.env.NEXT_PUBLIC_OAUTH_PATH

/** @type {import('next').NextConfig} */
const nextConfig = {
  ...(isProdEnv
    ? {}
    : {
        // ** Just for development
        async rewrites() {
          return {
            fallback: [
              {
                source: '/api/:path*',
                destination: `${apiUrl}/api/:path*`
              },
              {
                source: '/configs',
                destination: `${apiUrl}/configs`
              },
              {
                source: `${oauthPath}`,
                destination: `${oauthUri}${oauthPath}`
              }
            ]
          }
        }
      }),
  output: process.env.OUTPUT_MODE || 'standalone',
  distDir: 'dist',
  trailingSlash: false,
  reactStrictMode: false
}

module.exports = nextConfig