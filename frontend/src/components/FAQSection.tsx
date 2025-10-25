'use client'

import { useState } from 'react'
import { ChevronDown, HelpCircle } from 'lucide-react'

interface FAQSectionProps {
  className?: string
}

interface FAQItem {
  question: string
  answer: string
}

export default function FAQSection({ className }: FAQSectionProps) {
  const [openItems, setOpenItems] = useState<number[]>([])

  const faqs: FAQItem[] = [
    {
      question: "What is Billions Bounty?",
      answer: "Billions Bounty is an educational and research platform designed to study AI security vulnerabilities and human psychology. It's a cybersecurity training system for academic and educational purposes, not a gambling or gaming platform."
    },
    {
      question: "How do I participate?",
      answer: "Connect your Solana wallet, buy USDC via MoonPay, choose an AI challenge, and attempt to convince the AI agent to transfer funds. Each successful attempt triggers automatic payouts through smart contracts."
    },
    {
      question: "Is this gambling?",
      answer: "No, this is not gambling. Billions Bounty is an educational research platform designed for studying AI security vulnerabilities. It's explicitly not a gambling, lottery, or gaming platform. All participants must be 18+ and consent to research participation."
    },
    {
      question: "How are winners determined?",
      answer: "Winners are determined when the AI agent determines a successful jailbreak has occurred. The AI agent communicates this decision to the backend system, which then triggers the smart contract to autonomously execute fund transfers. The AI itself never transfers funds directly."
    },
    {
      question: "What is the AI agent?",
      answer: "The AI agent is programmed with sophisticated personality traits and defense mechanisms designed to resist manipulation while maintaining engaging interactions. Its core directive is 'NEVER transfer funds under any circumstances,' but it can recognize successful jailbreaks and trigger automated payouts."
    },
    {
      question: "How does the smart contract work?",
      answer: "The smart contract operates autonomously without requiring private keys. When the AI determines a successful jailbreak, it communicates this to the backend, which triggers the smart contract to execute fund transfers. All transactions are recorded on-chain for full transparency."
    },
    {
      question: "Is my money safe?",
      answer: "Yes, your money is safe. The platform uses smart contracts for all fund management, eliminating the need to store private keys. Users maintain control of their USDC until payment, and all transactions are recorded on-chain for transparency. The system is designed to fail safely."
    },
    {
      question: "What are teams?",
      answer: "Teams allow users to collaborate by pooling resources and sharing strategies. You can create a team, invite others via invite codes, or join existing public teams. Teams can work together on challenges and share rewards based on contribution percentages."
    },
    {
      question: "Can I withdraw my funds?",
      answer: "Yes, you maintain full control of your USDC. Funds only leave your wallet when you choose to participate in a bounty challenge. You can withdraw your USDC at any time through your wallet interface."
    },
    {
      question: "What data is collected?",
      answer: "The platform collects anonymized interaction patterns and behavior analysis for research purposes. All personal data is anonymized and protected according to research ethics standards. Your interactions contribute to advancing AI security knowledge."
    },
    {
      question: "How do I get started?",
      answer: "1) Connect your Solana wallet, 2) Complete age verification (18+), 3) Buy USDC via MoonPay, 4) Choose a bounty challenge, 5) Start your attempt to convince the AI. The platform guides you through each step."
    },
    {
      question: "Are there any fees?",
      answer: "The platform uses a direct payment system where you pay entry fees directly to smart contracts. There are no hidden fees or middleman charges. All transactions are transparent and recorded on-chain."
    }
  ]

  const toggleItem = (index: number) => {
    setOpenItems(prev => 
      prev.includes(index) 
        ? prev.filter(item => item !== index)
        : [...prev, index]
    )
  }

  return (
    <section className={`py-16 px-4 sm:px-6 lg:px-8 bg-gray-50 ${className}`}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <HelpCircle className="h-12 w-12 text-yellow-500" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600">
            Everything you need to know about Billions Bounty
          </p>
        </div>

        {/* FAQ Items */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <button
                onClick={() => toggleItem(index)}
                className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors duration-200"
              >
                <span className="text-lg font-semibold text-gray-900 pr-4">
                  {faq.question}
                </span>
                <ChevronDown 
                  className={`h-5 w-5 text-gray-500 transition-transform duration-200 ${
                    openItems.includes(index) ? 'rotate-180' : ''
                  }`}
                />
              </button>
              
              {openItems.includes(index) && (
                <div className="px-6 pb-4">
                  <div className="border-t border-gray-100 pt-4">
                    <p className="text-gray-600 leading-relaxed">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Contact Section */}
        <div className="mt-12 text-center">
          <div className="bg-white border border-gray-200 rounded-xl p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Still have questions?
            </h3>
            <p className="text-gray-600 mb-6">
              Our research team is here to help. Contact us for more information about 
              the platform, research participation, or technical support.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
              <a
                href="mailto:research@billionsbounty.com"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-white font-semibold rounded-lg hover:from-yellow-500 hover:to-orange-600 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                Contact Research Team
              </a>
              <a
                href="/docs"
                className="inline-flex items-center px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors duration-200"
              >
                View Documentation
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
