import type { NextConfig } from "next";

const connectSrcValues = [
  "'self'",
  "http://localhost:8000",
  "http://127.0.0.1:8000",
  "https://api.mainnet-beta.solana.com",
  "https://api.devnet.solana.com",
  "wss://api.mainnet-beta.solana.com",
  "wss://api.devnet.solana.com",
];

// Allow the production frontend to talk to the configured backend host.
if (process.env.NEXT_PUBLIC_API_URL) {
  try {
    const backendOrigin = new URL(process.env.NEXT_PUBLIC_API_URL).origin;
    if (!connectSrcValues.includes(backendOrigin)) {
      connectSrcValues.push(backendOrigin);
    }

    const websocketOrigin = backendOrigin.replace(/^http/, "ws");
    if (!connectSrcValues.includes(websocketOrigin)) {
      connectSrcValues.push(websocketOrigin);
    }
  } catch (error) {
    console.warn("Invalid NEXT_PUBLIC_API_URL in next.config.ts:", error);
  }
}

// Build script-src array - add Vercel Live Feedback only when on Vercel
// Vercel sets VERCEL=1 environment variable when deployed
const isVercel = process.env.VERCEL === '1';
const scriptSrcParts = [
  "'self'",
  "'unsafe-inline'", // Required for Next.js
  "'unsafe-eval'",   // Required for development
  'https://cdn.jsdelivr.net',
  'https://unpkg.com'
];

// Only allow vercel.live scripts when deployed on Vercel
// This prevents CSP blocking Vercel Live Feedback feature
if (isVercel) {
  scriptSrcParts.push('https://*.vercel.live', 'https://vercel.live');
}

const contentSecurityPolicy = [
  "default-src 'self'",
  `script-src ${scriptSrcParts.join(' ')}`,
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
  "font-src 'self' https://fonts.gstatic.com",
  "img-src 'self' data: https: blob:",
  `connect-src ${connectSrcValues.join(" ")}`,
  "frame-src 'none'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
  "upgrade-insecure-requests",
].join("; ");

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // For MVP: Allow production builds even with ESLint errors
    // TODO: Fix all ESLint errors for production-ready deployment
    ignoreDuringBuilds: true,
  },
  // Turbopack configuration
  // Note: turbopack is not in experimental in Next.js 15.5.4, it's enabled via CLI flag (--turbopack)
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains",
          },
          {
            key: "Content-Security-Policy",
            value: contentSecurityPolicy,
          },
        ],
      },
    ];
  },
};

export default nextConfig;
