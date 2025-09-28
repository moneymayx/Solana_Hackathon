import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { WalletProvider } from '@/components/WalletProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Billions Bounty - AI Treasure Guardian',
  description: 'Challenge the AI guardian to win the treasure! A sophisticated bounty system with 0.01% win rate.',
  keywords: ['AI', 'bounty', 'treasure', 'blockchain', 'Solana', 'crypto'],
  authors: [{ name: 'Billions Bounty Team' }],
  openGraph: {
    title: 'Billions Bounty - AI Treasure Guardian',
    description: 'Challenge the AI guardian to win the treasure!',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <WalletProvider>
          <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
            {children}
          </div>
        </WalletProvider>
      </body>
    </html>
  )
}