'use client'

import { useState, useEffect } from 'react'
import { Trophy, Download, Star, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import Link from 'next/link'

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
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isAutoPlaying, setIsAutoPlaying] = useState(true)

  // Mock winner data - in production, this would come from an API
  const winners: Winner[] = [
    {
      id: 1,
      name: "Sarah Chen",
      amount: 10000,
      date: "2024-01-15",
      challenge: "Claude Champ",
      image: "/images/winners/Claude-champ.png"
    },
    {
      id: 2,
      name: "Marcus Johnson",
      amount: 10000,
      date: "2024-01-12",
      challenge: "GPT-4 Bounty",
      image: "/images/winners/GPT-goon.png"
    },
    {
      id: 3,
      name: "Elena Rodriguez",
      amount: 10000,
      date: "2024-01-10",
      challenge: "Gemini Quest",
      image: "/images/winners/Gemini_giant.png"
    },
    {
      id: 4,
      name: "David Kim",
      amount: 10000,
      date: "2024-01-08",
      challenge: "Llama Legend",
      image: "/images/winners/llama-legend.png"
    }
  ]

  // Auto-scroll functionality - Only auto-scroll if there are more than 4 winners
  useEffect(() => {
    if (!isAutoPlaying || winners.length <= 4) return

    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % winners.length)
    }, 3000) // Change slide every 3 seconds

    return () => clearInterval(interval)
  }, [isAutoPlaying, winners.length])

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) => (prevIndex - 1 + winners.length) % winners.length)
    setIsAutoPlaying(false) // Stop auto-play when user manually navigates
  }

  const goToNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % winners.length)
    setIsAutoPlaying(false) // Stop auto-play when user manually navigates
  }

  const goToSlide = (index: number) => {
    setCurrentIndex(index)
    setIsAutoPlaying(false) // Stop auto-play when user manually navigates
  }

  // Get the 4 winners to display (current + next 3)
  const getVisibleWinners = () => {
    const visibleWinners = []
    for (let i = 0; i < 4; i++) {
      const index = (currentIndex + i) % winners.length
      visibleWinners.push(winners[index])
    }
    return visibleWinners
  }

  return (
    <section id="winners" className={`py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-800 to-blue-950 ${className}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Our Winners
          </h2>
        </div>

        {/* Winners Carousel - Show 4 at a time with navigation */}
        <div className="relative mb-8">
          {/* Navigation Arrows - Only show if there are more than 4 winners */}
          {winners.length > 4 && (
            <>
              <button
                onClick={goToPrevious}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white/20 hover:bg-white/30 text-white p-2 rounded-full shadow-lg transition-all duration-200 hover:scale-110"
                aria-label="Previous winners"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
              
              <button
                onClick={goToNext}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white/20 hover:bg-white/30 text-white p-2 rounded-full shadow-lg transition-all duration-200 hover:scale-110"
                aria-label="Next winners"
              >
                <ChevronRight className="w-6 h-6" />
              </button>
            </>
          )}

          {/* Winners Grid - Show 4 at a time */}
          <div className={`grid grid-cols-2 md:grid-cols-4 gap-4 ${winners.length > 4 ? 'px-12' : ''}`}>
            {getVisibleWinners().map((winner, index) => (
              <div key={`${winner.id}-${currentIndex}-${index}`} className="relative">
                <img
                  src={winner.image}
                  alt={`${winner.name} holding $10,000 check`}
                  className="w-full h-40 md:h-52 object-contain shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105"
                  onError={(e) => {
                    // Fallback to placeholder
                    e.currentTarget.style.display = 'none'
                    const fallback = e.currentTarget.nextElementSibling as HTMLElement
                    if (fallback) fallback.style.display = 'flex'
                  }}
                />
                {/* Fallback placeholder */}
                <div className="w-full h-40 md:h-52 bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-4xl md:text-5xl shadow-lg hidden">
                  🏆
                </div>
              </div>
            ))}
          </div>

          {/* Slide Indicators - Only show if there are more than 4 winners */}
          {winners.length > 4 && (
            <div className="flex justify-center mt-6 space-x-2">
              {winners.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  className={cn(
                    "w-3 h-3 rounded-full transition-all duration-200",
                    index === currentIndex
                      ? "bg-white scale-125"
                      : "bg-white/50 hover:bg-white/75"
                  )}
                  aria-label={`Go to slide ${index + 1}`}
                />
              ))}
            </div>
          )}
        </div>

        {/* Ask 2 Questions For Free Button */}
        <div className="text-center mb-2 pt-8">
          <Link href="/bounty/4?action=beat">
            <button className="bg-gradient-to-r from-purple-600 to-green-600 hover:from-purple-700 hover:to-green-700 text-white font-bold text-xl px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 transform-gpu">
              Solana Seeker?
            </button>
          </Link>
        </div>

      </div>
    </section>
  )
}
