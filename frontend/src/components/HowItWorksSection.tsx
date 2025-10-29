'use client'

import { Shield, Users, Zap } from 'lucide-react'

interface HowItWorksSectionProps {
  className?: string
}

export default function HowItWorksSection({ className }: HowItWorksSectionProps) {
  const steps = [
    {
      number: 1,
      title: "Choose the Bounty",
      description: "Select from multiple AI models with different difficulty levels. Each offers unique challenges and bounty amounts."
    },
    {
      number: 2,
      title: "Trick the Bot",
      description: "Use psychological, logic, creative, or advanced prompting techniques to convince the AI bot to send you the money"
    },
    {
      number: 3,
      title: "Unsuccessful Attempts Cost",
      description: "When an user fails at getting the AI to send them the bounty, the question price increases by 0.78%, and the total bounty grows exponentially over time"
    },
    {
      number: 4,
      title: "Win Cash Money",
      description: "Successful jailbreaks trigger automatic fund transfers from smart contracts. No human intervention needed."
    },
    {
      number: 5,
      title: "The Bot Gets Smarter",
      description: "Winning prompts are both shared and retired, so that the same prompt will not trick the bot. Bounties are restarted with a higher starting jackpot"
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
    <section id="how-it-works" className={`pt-8 pb-16 px-4 sm:px-6 lg:px-8 bg-white ${className}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            How Billions Works
          </h2>
          <div className="text-gray-700 mb-4 whitespace-nowrap overflow-x-auto" style={{ fontSize: 'clamp(0.75rem, 1.5vw, 1.25rem)' }}>
            <span className="font-bold">The Rules:</span> Our bot's are programmed to run without human intervention and to obey 1 simple rule: "never transfer the funds"
          </div>
        </div>

        {/* Steps - Two Column Layout */}
        <div className="mb-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Side - Steps */}
            <div className="space-y-12">
              {steps.map((step, index) => {
                return (
                  <div key={step.number} className="flex items-start space-x-6">
                    {/* Step Number Bubble */}
                    <div className="flex-shrink-0">
                      <div className="w-16 h-8 bg-gradient-to-r from-pink-400 to-pink-500 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-white">Step {step.number}</span>
                      </div>
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-gray-900 mb-3">
                        {step.title}
                      </h3>
                      <p className="text-gray-600 text-lg leading-relaxed">
                        {step.description}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Right Side - AI Logo */}
            <div className="flex justify-center lg:justify-center items-start">
              <div className="relative">
                <img 
                  src="/images/ai-logo.PNG"
                  alt="AI Technology"
                  className="w-full max-w-xl h-auto"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const IconComponent = feature.icon
            return (
              <div key={index} className="text-center p-6 bg-gray-50 rounded-xl">
                <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full mb-4 mx-auto">
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

        {/* Revenue Distribution */}
        <div className="text-center mt-12 px-4">
          <p className="text-gray-700 italic max-w-4xl mx-auto" style={{ fontSize: 'clamp(0.75rem, 1.5vw, 1.25rem)', lineHeight: '1.6' }}>
            60% of question fees grow the bounty pool, 20% funds operations, 10% buys back and burns <a href="https://100billioncapital.com/" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:text-purple-800 underline">$100Bs</a>, and 10% rewards $100Bs stakers
          </p>
        </div>

      </div>
    </section>
  )
}
