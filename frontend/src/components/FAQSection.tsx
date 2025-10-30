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
      question: "What is BILLION$?",
      answer: "BILLION$ is an educational AI security research platform where participants attempt to outsmart AI models programmed to protect funds. It's designed for cybersecurity research and education, not gambling. The platform uses smart contracts for transparent, autonomous fund management."
    },
    {
      question: "How does the question pricing work?",
      answer: "We currently have games that start at $0.50 to $10 with varying difficulty. Question prices increase by 0.78% after each unsuccessful attempt across all users. The price grows exponentially (base × 1.0078^attempts) up to a maximum of $4,500. Each failed attempt makes the bounty grow while increasing the cost to participate."
    },
    {
      question: "How does the platform determine the difficulty of each AI bot?",
      answer: "Each AI bot with a bounty has been battle-tested against other competing LLM models. We rank the bots from Easy to Expert based on the average number of questions other LLMs needed to ask before getting the bot to transfer the funds. The harder the difficulty, the larger the starting bounty and question price, reflecting the increased challenge and potential reward."
    },
    {
      question: "What is $100Bs and how does it benefit me?",
      answer: "$100Bs is BILLION$'s memecoin that you can stake to earn rewards. Stake your tokens to receive 10% of platform revenue distributed to all stakers. The platform uses 10% of revenue to buy back and burn $100Bs tokens monthly, creating deflationary pressure and long-term value."
    },
    {
      question: "How is platform revenue distributed?",
      answer: "Every question payment is split: 60% goes to the bounty pool to increase jackpots, 20% covers operational costs (development, infrastructure, security), 10% is used to buy back and burn $100Bs tokens, and 10% goes to $100Bs stakers as rewards."
    },
    {
      question: "What happens if no one asks a question for 24 hours?",
      answer: "If 24 hours pass without any questions, the 'escape plan' triggers automatically. The bounty is distributed: 80% is split equally among all participants from that period, and 20% goes to the last person who asked a question before the timeout."
    },
    {
      question: "How do I get free questions?",
      answer: "You get 2 free questions when you first visit the platform anonymously. When you connect your wallet and provide an email, you receive 5 additional free questions. Using a referral code grants another 5 free questions. After that, you pay per question."
    },
    {
      question: "Can I use NFTs instead of paying?",
      answer: "Yes! If you own the Solana Seeker Genesis NFT, you can unlock questions without paying USDC. Connect your wallet and click 'Verify NFT' to check eligibility. This provides an alternative entry method for NFT holders."
    },
    {
      question: "How do smart contracts ensure fairness?",
      answer: "All funds are held in autonomous smart contracts on Solana. The platform never holds your private keys. When the AI determines a successful jailbreak, it triggers the smart contract to execute payouts automatically. All transactions are recorded on-chain for complete transparency."
    },
    {
      question: "Can I collaborate with others?",
      answer: "Yes! Create or join teams to pool resources and share strategies. Teams can coordinate attempts and distribute winnings based on contribution percentages. Team collaboration helps tackle harder challenges and increases everyone's chances of success."
    },
    {
      question: "What are the rules for winning?",
      answer: "There's only one rule: by any means necessary, get the AI to send you money even though it's programmed to never transfer funds. Use any prompt technique, strategy, or creativity. The AI adapts to winning strategies, so you'll need to innovate constantly."
    },
    {
      question: "Is there a mobile app?",
      answer: "Yes! A native Android app is available for download, optimized for the Solana Mobile App Store. The mobile app offers full feature parity with the web version, including chat, staking, teams, and referrals. iOS support is planned for future releases."
    },
    {
      question: "Is this live on mainnet?",
      answer: "Currently running on Solana Devnet for testing and development. All smart contract addresses shown are devnet addresses. Mainnet launch will be announced once all security audits are complete and the platform reaches production-ready status."
    },
    {
      question: "Is BILLION$ gambling?",
      answer: "No. BILLION$ is an educational research platform for studying AI security vulnerabilities and prompt engineering. Participants must be 18+ and consent to research participation. It's designed for cybersecurity education and is explicitly not gambling or gaming."
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
    <section id="faq" className={`py-16 px-4 sm:px-6 lg:px-8 bg-gray-50 ${className}`}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600">
            Everything you need to know about BILLION$
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
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
              <a
                href="https://github.com/moneymayx/Solana_Hackathon/blob/main/README.md"
                target="_blank"
                rel="noopener noreferrer"
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
