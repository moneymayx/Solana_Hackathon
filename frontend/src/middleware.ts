import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(_request: NextRequest) {
  const response = NextResponse.next()
  
  // Content Security Policy
  const backendUrl = process.env.NEXT_PUBLIC_API_URL
  const connectSrcValues = [
    "'self'",
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://api.mainnet-beta.solana.com',
    'https://api.devnet.solana.com',
    'wss://api.mainnet-beta.solana.com',
    'wss://api.devnet.solana.com',
  ]

  if (backendUrl) {
    try {
      const origin = new URL(backendUrl).origin
      if (!connectSrcValues.includes(origin)) {
        // Allow fetches to the configured backend host so production deployments work.
        connectSrcValues.push(origin)
      }
    } catch (error) {
      console.warn('Invalid NEXT_PUBLIC_API_URL provided to middleware:', error)
    }
  }

  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https: blob:",
    `connect-src ${connectSrcValues.join(' ')}`,
    "frame-src 'none'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "upgrade-insecure-requests"
  ].join('; ')

  // Security Headers
  response.headers.set('Content-Security-Policy', csp)
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
  
  return response
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
