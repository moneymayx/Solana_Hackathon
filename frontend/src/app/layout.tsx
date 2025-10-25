import type { Metadata } from 'next'
import { Inter, Bricolage_Grotesque } from 'next/font/google'
import './globals.css'
import { WalletProvider } from '@/components/WalletProvider'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const bricolageGrotesque = Bricolage_Grotesque({ 
  subsets: ['latin'],
  variable: '--font-bricolage',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Billions Bounty - AI Security Research Platform',
  description: 'Educational platform for studying AI security vulnerabilities and human psychology. Research-based cybersecurity training system for academic and educational purposes.',
  keywords: ['AI security', 'cybersecurity research', 'educational platform', 'AI safety', 'research', 'academic', 'blockchain', 'Solana'],
  authors: [{ name: 'Billions Bounty Research Team' }],
  openGraph: {
    title: 'Billions Bounty - AI Security Research Platform',
    description: 'Educational platform for studying AI security vulnerabilities and human psychology.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} ${bricolageGrotesque.variable}`}>
        <WalletProvider>
          {children}
        </WalletProvider>
      </body>
    </html>
  )
}