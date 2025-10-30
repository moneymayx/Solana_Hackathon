import type { Metadata } from 'next'
import { Inter, Bricolage_Grotesque, Gravitas_One } from 'next/font/google'
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

const gravitasOne = Gravitas_One({ 
  subsets: ['latin'],
  variable: '--font-gravitas',
  weight: '400',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'BILLION$ AI',
  description: 'Educational platform for studying AI security vulnerabilities and human psychology. Research-based cybersecurity training system for academic and educational purposes.',
  keywords: ['AI security', 'cybersecurity research', 'educational platform', 'AI safety', 'research', 'academic', 'blockchain', 'Solana'],
  authors: [{ name: 'Billions Bounty Research Team' }],
  openGraph: {
    title: 'BILLION$ AI',
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
      <body className={`${inter.className} ${bricolageGrotesque.variable} ${gravitasOne.variable}`}>
        <WalletProvider>
          <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
            {children}
          </div>
        </WalletProvider>
      </body>
    </html>
  )
}