'use client'

/**
 * Features Page
 * 
 * Showcase all platform enhancements
 */

import Link from 'next/link'
import Navigation from '@/components/Navigation'

export default function FeaturesPage() {
  const features = [
    {
      phase: 'Phase 1',
      title: 'Smart AI Context',
      icon: '🧠',
      description: 'AI remembers ALL historical attacks using semantic search',
      benefits: [
        'Pattern recognition across all users',
        'Semantic search for similar attacks',
        'Automatic context summarization',
        'Multi-tier context strategy'
      ],
      link: '/test-api',
      linkText: 'Test Context API',
      color: 'from-blue-600 to-cyan-600'
    },
    {
      phase: 'Phase 2',
      title: '$100Bs Token Economics',
      icon: '💎',
      description: 'Real utility with discounts and revenue-based staking',
      benefits: [
        '10-50% discount on queries',
        '30% of revenue to stakers',
        'Tiered staking (30/60/90 days)',
        '5% revenue for token buyback'
      ],
      link: '/token',
      linkText: 'View Token Dashboard',
      color: 'from-green-600 to-emerald-600'
    },
    {
      phase: 'Phase 3',
      title: 'Team Collaboration',
      icon: '👥',
      description: 'Form teams, pool resources, and share strategies',
      benefits: [
        'Create or join teams',
        'Shared funding pool',
        'Internal team chat',
        'Proportional prize splitting'
      ],
      link: '/teams',
      linkText: 'Browse Teams',
      color: 'from-purple-600 to-pink-600'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-900">
      <Navigation />

      {/* Hero */}
      <div className="bg-gradient-to-b from-gray-800/50 to-gray-900 py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Platform Enhancements
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Three major upgrades make Billions Bounty the most advanced AI jailbreak challenge platform
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/token"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors"
            >
              Get Started →
            </Link>
            <Link
              href="/test-api"
              className="bg-gray-700 hover:bg-gray-600 text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors"
            >
              Test APIs
            </Link>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="container mx-auto px-4 py-16">
        <div className="space-y-12">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Left: Info */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-5xl">{feature.icon}</span>
                    <div>
                      <p className="text-sm text-gray-400 font-medium">{feature.phase}</p>
                      <h2 className="text-3xl font-bold text-white">{feature.title}</h2>
                    </div>
                  </div>
                  
                  <p className="text-gray-300 text-lg mb-6">{feature.description}</p>
                  
                  <Link
                    href={feature.link}
                    className={`inline-block bg-gradient-to-r ${feature.color} text-white px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity`}
                  >
                    {feature.linkText} →
                  </Link>
                </div>

                {/* Right: Benefits */}
                <div>
                  <h3 className="text-xl font-bold text-white mb-4">Key Benefits</h3>
                  <ul className="space-y-3">
                    {feature.benefits.map((benefit, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <span className="text-green-400 mt-1">✓</span>
                        <span className="text-gray-300">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="bg-gray-800/50 backdrop-blur-sm border-y border-gray-700 py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-4xl font-bold text-blue-400 mb-2">50+</p>
              <p className="text-gray-400">API Endpoints</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-green-400 mb-2">43</p>
              <p className="text-gray-400">Database Tables</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-purple-400 mb-2">6</p>
              <p className="text-gray-400">Services</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-pink-400 mb-2">100%</p>
              <p className="text-gray-400">Production Ready</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="container mx-auto px-4 py-16 text-center">
        <h2 className="text-4xl font-bold text-white mb-4">Ready to Explore?</h2>
        <p className="text-gray-300 mb-8 text-lg">
          All features are live and ready to use
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/token"
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity"
          >
            💎 Token Dashboard
          </Link>
          <Link
            href="/teams"
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity"
          >
            👥 Browse Teams
          </Link>
        </div>
      </div>
    </div>
  )
}












