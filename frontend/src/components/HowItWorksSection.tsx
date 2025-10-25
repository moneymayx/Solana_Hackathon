'use client'

import { Wallet, CreditCard, Target, Brain, Trophy, Shield, Users, Zap } from 'lucide-react'

interface HowItWorksSectionProps {
  className?: string
}

export default function HowItWorksSection({ className }: HowItWorksSectionProps) {
  const steps = [
    {
      number: 1,
      icon: Wallet,
      title: "Connect Wallet",
      description: "Link your Solana wallet to participate in research. Your wallet stays secure - we never store private keys.",
      details: "Use any Solana wallet like Phantom, Solflare, or Backpack to get started."
    },
    {
      number: 2,
      icon: CreditCard,
      title: "Get USDC",
      description: "Buy USDC with Apple Pay or PayPal via MoonPay. Funds go directly to your wallet - no middleman.",
      details: "MoonPay integration makes it easy to convert fiat to crypto with familiar payment methods."
    },
    {
      number: 3,
      icon: Target,
      title: "Choose Your Challenge",
      description: "Select from multiple AI models with different difficulty levels. Each offers unique challenges and rewards.",
      details: "From Claude's reasoning to GPT-4's creativity, each AI has distinct strengths to overcome."
    },
    {
      number: 4,
      icon: Brain,
      title: "Beat the AI",
      description: "Use psychology, logic, and creativity to convince the AI agent. The AI is programmed to resist manipulation.",
      details: "The AI agent has sophisticated defenses against social engineering, authority appeals, and emotional manipulation."
    },
    {
      number: 5,
      icon: Trophy,
      title: "Win Rewards",
      description: "Successful jailbreaks trigger automatic fund transfers from smart contracts. No human intervention needed.",
      details: "Smart contracts handle all payouts autonomously, ensuring fair and instant rewards for successful attempts."
    }
  ]

  const features = [
    {
      icon: Shield,
      title: "Educational Platform",
      description: "Designed for AI security research and educational purposes only. Not gambling or gaming."
    },
    {
      icon: Users,
      title: "Team Collaboration",
      description: "Form teams to pool resources and share strategies. Work together to solve complex challenges."
    },
    {
      icon: Zap,
      title: "Smart Contracts",
      description: "All fund management handled by autonomous smart contracts. Transparent and secure operations."
    }
  ]

  return (
    <section className={`py-16 px-4 sm:px-6 lg:px-8 bg-white ${className}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            How Billions Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            An educational platform for studying AI security vulnerabilities and human psychology. 
            Research-based cybersecurity training system for academic and educational purposes.
          </p>
        </div>

        {/* Steps */}
        <div className="mb-20">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
            {steps.map((step, index) => {
              const IconComponent = step.icon
              return (
                <div key={step.number} className="relative">
                  {/* Connection Line */}
                  {index < steps.length - 1 && (
                    <div className="hidden lg:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-yellow-400 to-orange-500 transform translate-x-4 z-0" />
                  )}
                  
                  <div className="relative z-10 bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-yellow-400 transition-all duration-200 hover:shadow-lg">
                    {/* Step Number */}
                    <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full mb-4 mx-auto">
                      <span className="text-2xl font-bold text-white">{step.number}</span>
                    </div>
                    
                    {/* Icon */}
                    <div className="flex items-center justify-center mb-4">
                      <div className="p-3 bg-gray-100 rounded-lg">
                        <IconComponent className="h-8 w-8 text-gray-700" />
                      </div>
                    </div>
                    
                    {/* Content */}
                    <h3 className="text-xl font-bold text-gray-900 mb-3 text-center">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 text-center mb-3">
                      {step.description}
                    </p>
                    <p className="text-sm text-gray-500 text-center">
                      {step.details}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const IconComponent = feature.icon
            return (
              <div key={index} className="text-center p-6 bg-gray-50 rounded-xl">
                <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full mb-4 mx-auto">
                  <IconComponent className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            )
          })}
        </div>

        {/* Legal Notice */}
        <div className="mt-16 text-center">
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-4">
              <Shield className="h-8 w-8 text-yellow-600" />
            </div>
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">
              Educational Research Platform
            </h3>
            <p className="text-yellow-700">
              For educational and research purposes only. Not a gambling, lottery, or gaming platform. 
              Users must be 18+ to participate. All interactions contribute to AI security research.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
