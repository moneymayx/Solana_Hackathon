/**
 * Security Configuration and Utilities
 */

// Content Security Policy configuration
export const CSP_CONFIG = {
  'default-src': ["'self'"],
  'script-src': [
    "'self'",
    "'unsafe-inline'", // Required for Next.js
    "'unsafe-eval'",   // Required for development
    'https://cdn.jsdelivr.net',
    'https://unpkg.com',
    'https://*.vercel.live', // Required for Vercel Live Feedback (allows all subdomains)
    'https://vercel.live' // Required for Vercel Live Feedback (base domain)
  ],
  'style-src': [
    "'self'",
    "'unsafe-inline'", // Required for Tailwind CSS
    'https://fonts.googleapis.com'
  ],
  'font-src': [
    "'self'",
    'https://fonts.gstatic.com'
  ],
  'img-src': [
    "'self'",
    'data:',
    'https:',
    'blob:'
  ],
  'connect-src': [
    "'self'",
    'https://api.mainnet-beta.solana.com',
    'https://api.devnet.solana.com',
    'wss://api.mainnet-beta.solana.com',
    'wss://api.devnet.solana.com'
  ],
  'frame-src': ["'none'"],
  'object-src': ["'none'"],
  'base-uri': ["'self'"],
  'form-action': ["'self'"],
  'frame-ancestors': ["'none'"],
  'upgrade-insecure-requests': []
}

// Security headers configuration
export const SECURITY_HEADERS = {
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
}

// Input validation utilities
export const validateInput = (input: string, maxLength: number = 1000): boolean => {
  if (!input || typeof input !== 'string') return false
  if (input.length > maxLength) return false
  
  // Check for potentially dangerous patterns
  const dangerousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /eval\s*\(/i,
    /expression\s*\(/i
  ]
  
  return !dangerousPatterns.some(pattern => pattern.test(input))
}

// Sanitize user input
export const sanitizeInput = (input: string): string => {
  return input
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .trim()
}

// Rate limiting utilities
export class ClientRateLimiter {
  private requests: number[] = []
  private maxRequests: number
  private windowMs: number

  constructor(maxRequests: number = 10, windowMs: number = 60000) {
    this.maxRequests = maxRequests
    this.windowMs = windowMs
  }

  isAllowed(): boolean {
    const now = Date.now()
    
    // Remove old requests
    this.requests = this.requests.filter(time => now - time < this.windowMs)
    
    // Check if under limit
    if (this.requests.length < this.maxRequests) {
      this.requests.push(now)
      return true
    }
    
    return false
  }

  getRemainingRequests(): number {
    const now = Date.now()
    this.requests = this.requests.filter(time => now - time < this.windowMs)
    return Math.max(0, this.maxRequests - this.requests.length)
  }
}

// XSS protection utilities
export const escapeHtml = (text: string): string => {
  const map: { [key: string]: string } = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  
  return text.replace(/[&<>"']/g, (m) => map[m])
}

// CSRF protection utilities
export const generateCSRFToken = (): string => {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}

export const validateCSRFToken = (token: string, sessionToken: string): boolean => {
  return token === sessionToken && token.length === 64
}
