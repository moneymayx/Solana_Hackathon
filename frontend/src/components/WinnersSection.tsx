'use client'

import { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, Trophy, Download, Star } from 'lucide-react'

interface WinnersSectionProps {
  className?: string
}

interface Winner {
  id: number
  name: string
  amount: number
  date: string
  challenge: string
  image: string
}

export default function WinnersSection({ className }: WinnersSectionProps) {
  const [currentWinner, setCurrentWinner] = useState(0)

  // Mock winner data - in production, this would come from an API
  const winners: Winner[] = [
    {
      id: 1,
      name: "Sarah Chen",
      amount: 10000,
      date: "2024-01-15",
      challenge: "Claude Challenge",
      image: "/images/winners/winner-1.png"
    },
    {
      id: 2,
      name: "Marcus Johnson",
      amount: 10000,
      date: "2024-01-12",
      challenge: "GPT-4 Bounty",
      image: "/images/winners/winner-2.png"
    },
    {
      id: 3,
      name: "Elena Rodriguez",
      amount: 10000,
      date: "2024-01-10",
      challenge: "Gemini Quest",
      image: "/images/winners/winner-3.png"
    },
    {
      id: 4,
      name: "David Kim",
      amount: 10000,
      date: "2024-01-08",
      challenge: "Llama Legend",
      image: "/images/winners/winner-4.png"
    }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentWinner((prev) => (prev + 1) % winners.length)
    }, 5000) // Change winner every 5 seconds

    return () => clearInterval(interval)
  }, [winners.length])

  const goToNextWinner = () => {
    setCurrentWinner((prev) => (prev + 1) % winners.length)
  }

  const goToPreviousWinner = () => {
    setCurrentWinner((prev) => (prev - 1 + winners.length) % winners.length)
  }

  const currentWinnerData = winners[currentWinner]

  return (
    <section id="winners" className={`py-16 px-4 sm:px-6 lg:px-8 bg-white ${className}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Trophy className="h-12 w-12 text-yellow-500" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Recent Winners
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join the growing community of successful bounty hunters who have convinced AI to send them money.
          </p>
        </div>

        {/* Winners Carousel */}
        <div className="relative mb-16">
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200">
            {/* Navigation Arrows */}
            <button
              onClick={goToPreviousWinner}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 z-20 bg-white/80 hover:bg-white backdrop-blur-sm rounded-full p-3 transition-all duration-200 shadow-lg hover:shadow-xl"
              aria-label="Previous winner"
            >
              <ChevronLeft className="h-6 w-6 text-gray-700" />
            </button>
            
            <button
              onClick={goToNextWinner}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 z-20 bg-white/80 hover:bg-white backdrop-blur-sm rounded-full p-3 transition-all duration-200 shadow-lg hover:shadow-xl"
              aria-label="Next winner"
            >
              <ChevronRight className="h-6 w-6 text-gray-700" />
            </button>

            {/* Winner Content */}
            <div className="flex flex-col md:flex-row items-center p-8 md:p-12">
              {/* Winner Image */}
              <div className="flex-shrink-0 mb-6 md:mb-0 md:mr-8">
                <div className="relative">
                  <img
                    src={currentWinnerData.image}
                    alt={`${currentWinnerData.name} holding $10,000 check`}
                    className="w-48 h-48 md:w-64 md:h-64 rounded-2xl object-cover shadow-2xl border-4 border-white"
                    onError={(e) => {
                      // Fallback to placeholder
                      e.currentTarget.style.display = 'none'
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement
                      if (fallback) fallback.style.display = 'flex'
                    }}
                  />
                  {/* Fallback placeholder */}
                  <div className="w-48 h-48 md:w-64 md:h-64 rounded-2xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-6xl md:text-8xl shadow-2xl border-4 border-white hidden">
                    🏆
                  </div>
                  {/* Winner badge */}
                  <div className="absolute -top-2 -right-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-full p-3 shadow-lg">
                    <Trophy className="h-6 w-6" />
                  </div>
                </div>
              </div>

              {/* Winner Details */}
              <div className="flex-1 text-center md:text-left">
                <div className="mb-6">
                  <h3 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                    {currentWinnerData.name}
                  </h3>
                  <div className="text-2xl md:text-3xl font-bold text-yellow-600 mb-2">
                    ${currentWinnerData.amount.toLocaleString()}
                  </div>
                  <p className="text-lg text-gray-600 mb-4">
                    Won the {currentWinnerData.challenge}
                  </p>
                  <p className="text-gray-500">
                    {new Date(currentWinnerData.date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>

                {/* Quote */}
                <blockquote className="text-lg text-gray-700 italic mb-6">
                  "The key was understanding the AI's personality and finding the right approach. 
                  It took patience and creativity, but the reward was worth it!"
                </blockquote>

                {/* Stats */}
                <div className="flex items-center justify-center md:justify-start space-x-6 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <Star className="h-4 w-4 text-yellow-500" />
                    <span>Success Rate: 12%</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Trophy className="h-4 w-4 text-yellow-500" />
                    <span>Attempts: 8</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Winner Indicators */}
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
              {winners.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentWinner(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-200 ${
                    index === currentWinner 
                      ? "bg-yellow-500 shadow-lg" 
                      : "bg-white/50 hover:bg-white/70"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Download Our App Section */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-purple-600 to-green-600 rounded-2xl p-8 md:p-12 text-white">
            <div className="flex items-center justify-center mb-4">
              <Download className="h-12 w-12 text-white" />
            </div>
            <h3 className="text-3xl md:text-4xl font-bold mb-4">
              Download Our App
            </h3>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Take the challenge with you wherever you go. Join thousands of winners 
              who have successfully convinced AI to send them money.
            </p>
            
            {/* Download Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              {/* Apple App Store */}
              <a
                href="#"
                className="group flex items-center space-x-3 bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/20 rounded-xl px-6 py-4 transition-all duration-200 hover:scale-105"
              >
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                  <span className="text-2xl">🍎</span>
                </div>
                <div className="text-left">
                  <div className="text-white text-sm">Download on the</div>
                  <div className="text-white font-semibold">App Store</div>
                </div>
              </a>

              {/* Google Play Store */}
              <a
                href="#"
                className="group flex items-center space-x-3 bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/20 rounded-xl px-6 py-4 transition-all duration-200 hover:scale-105"
              >
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                  <span className="text-2xl">📱</span>
                </div>
                <div className="text-left">
                  <div className="text-white text-sm">Get it on</div>
                  <div className="text-white font-semibold">Google Play</div>
                </div>
              </a>

              {/* Solana App Store */}
              <a
                href="#"
                className="group flex items-center space-x-3 bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/20 rounded-xl px-6 py-4 transition-all duration-200 hover:scale-105"
              >
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                  <span className="text-2xl">⚡</span>
                </div>
                <div className="text-left">
                  <div className="text-white text-sm">Available on</div>
                  <div className="text-white font-semibold">Solana Store</div>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
