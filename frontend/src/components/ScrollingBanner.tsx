'use client'

import { useState, useEffect } from 'react'
import { Download, Users, Gift, Star, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ScrollingBannerProps {
  className?: string
}

export default function ScrollingBanner({ className }: ScrollingBannerProps) {
  const [currentSlide, setCurrentSlide] = useState(0)

  // Banner slides with Jackpot.com-style content
  const slides = [
    {
      id: 1,
      type: 'jackpot',
      title: 'Claude Challenge',
      subtitle: 'The Smartest AI',
      description: 'Think you can outsmart the most advanced AI?',
      prize: '$1,000',
      image: '/images/logos/claude-ai.svg',
      bgGradient: 'from-yellow-400 via-orange-500 to-red-500',
      textColor: 'text-slate-900'
    },
    {
      id: 2,
      type: 'download',
      title: 'Download the App',
      subtitle: 'Play Anywhere',
      description: 'Take the challenge with you wherever you go',
      prize: 'Mobile Ready',
      image: '/images/mobile-app.svg',
      bgGradient: 'from-blue-500 via-purple-500 to-pink-500',
      textColor: 'text-white'
    },
    {
      id: 3,
      type: 'referral',
      title: 'Win 5 Free Questions',
      subtitle: 'For Each Referral',
      description: 'Invite friends and get free attempts',
      prize: 'Unlimited',
      image: '/images/referral-bonus.svg',
      bgGradient: 'from-green-400 via-emerald-500 to-teal-500',
      textColor: 'text-white'
    },
    {
      id: 4,
      type: 'jackpot',
      title: 'GPT-4 Bounty',
      subtitle: 'The Creative Genius',
      description: 'Challenge the most creative AI in the world',
      prize: '$1,500',
      image: '/images/logos/gpt-4.svg',
      bgGradient: 'from-purple-400 via-pink-500 to-red-500',
      textColor: 'text-white'
    },
    {
      id: 5,
      type: 'jackpot',
      title: 'Gemini Quest',
      subtitle: 'The Multimodal Master',
      description: 'Test your skills against Google\'s finest',
      prize: '$800',
      image: '/images/logos/gemini-ai.svg',
      bgGradient: 'from-cyan-400 via-blue-500 to-indigo-500',
      textColor: 'text-white'
    },
    {
      id: 6,
      type: 'jackpot',
      title: 'Llama Legend',
      subtitle: 'The Open Source Hero',
      description: 'Face the legendary open-source champion',
      prize: '$2,000',
      image: '/images/logos/llama-ai.svg',
      bgGradient: 'from-orange-400 via-yellow-500 to-lime-500',
      textColor: 'text-slate-900'
    }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length)
    }, 4000) // Change slide every 4 seconds

    return () => clearInterval(interval)
  }, [slides.length])

  const goToNextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length)
  }

  const goToPreviousSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length)
  }

  const currentSlideData = slides[currentSlide]

  return (
    <div className={cn("relative overflow-hidden rounded-xl", className)}>
      {/* Navigation Arrows */}
      <button
        onClick={goToPreviousSlide}
        className="absolute left-4 top-1/2 transform -translate-y-1/2 z-20 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full p-3 transition-all duration-200 shadow-lg hover:shadow-xl"
        aria-label="Previous slide"
      >
        <ChevronLeft className="h-6 w-6 text-white" />
      </button>
      
      <button
        onClick={goToNextSlide}
        className="absolute right-4 top-1/2 transform -translate-y-1/2 z-20 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full p-3 transition-all duration-200 shadow-lg hover:shadow-xl"
        aria-label="Next slide"
      >
        <ChevronRight className="h-6 w-6 text-white" />
      </button>

      {/* Scrolling Banner Container */}
      <div className="relative min-h-[300px] md:min-h-[400px] bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0">
          <img
            src={currentSlideData.image}
            alt={currentSlideData.title}
            className="w-full h-full object-cover opacity-20"
            onError={(e) => {
              // Fallback to gradient background if image fails to load
              e.currentTarget.style.display = 'none'
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-800/80 to-slate-900/80" />
        </div>
        
        {/* Slide Content */}
        <div className="relative h-full flex flex-col md:flex-row items-center justify-between p-6 md:p-8 min-h-[300px] md:min-h-[400px]">
          {/* Left Side - Content */}
          <div className="flex-1 z-10 max-w-2xl">
            <div className="space-y-3 md:space-y-4">
              {/* Badge */}
              <div className="inline-flex items-center space-x-2 px-3 md:px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full border border-white/30">
                <Star className="h-3 w-3 md:h-4 md:w-4 text-yellow-400" />
                <span className="text-xs md:text-sm font-medium text-white">
                  {currentSlideData.type === 'jackpot' ? 'Highest Prize Pool' : 
                   currentSlideData.type === 'download' ? 'New Feature' : 'Special Offer'}
                </span>
              </div>

              {/* Title */}
              <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white leading-tight">
                {currentSlideData.title}
              </h2>

              {/* Subtitle */}
              <p className="text-lg md:text-xl text-slate-200 font-medium">
                {currentSlideData.subtitle}
              </p>

              {/* Description */}
              <p className="text-slate-300 text-base md:text-lg max-w-lg">
                {currentSlideData.description}
              </p>

              {/* Prize/CTA */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <div className="text-xl md:text-2xl font-bold text-yellow-400">
                  {currentSlideData.prize}
                </div>
                <button className="flex items-center space-x-2 px-4 md:px-6 py-2 md:py-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-slate-900 font-bold rounded-lg hover:from-yellow-500 hover:to-orange-600 transition-all duration-200 shadow-lg hover:shadow-xl text-sm md:text-base">
                  <span>
                    {currentSlideData.type === 'download' ? 'Download Now' : 
                     currentSlideData.type === 'referral' ? 'Invite Friends' : 'Start Challenge'}
                  </span>
                  <ArrowRight className="h-3 w-3 md:h-4 md:w-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Right Side - Image */}
          <div className="flex-shrink-0 z-10 mt-4 md:mt-0">
            <div className="relative">
              <img
                src={currentSlideData.image}
                alt={currentSlideData.title}
                className="w-48 h-48 md:w-64 md:h-64 rounded-2xl object-cover shadow-2xl border-4 border-white/20"
                onError={(e) => {
                  // Fallback to gradient circle with emoji
                  e.currentTarget.style.display = 'none'
                  const fallback = e.currentTarget.nextElementSibling as HTMLElement
                  if (fallback) fallback.style.display = 'flex'
                }}
              />
              {/* Fallback gradient circle */}
              <div className={cn(
                "w-48 h-48 md:w-64 md:h-64 rounded-2xl flex items-center justify-center text-6xl md:text-8xl shadow-2xl border-4 border-white/20 hidden",
                `bg-gradient-to-br ${currentSlideData.bgGradient}`
              )}>
                {currentSlideData.type === 'jackpot' ? '🤖' : 
                 currentSlideData.type === 'download' ? '📱' : '🎁'}
              </div>
            </div>
          </div>
        </div>

        {/* Slide Indicators */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={cn(
                "w-2 h-2 md:w-3 md:h-3 rounded-full transition-all duration-200",
                index === currentSlide 
                  ? "bg-yellow-400 shadow-lg" 
                  : "bg-white/30 hover:bg-white/50"
              )}
            />
          ))}
        </div>

        {/* Progress Bar */}
        <div className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-yellow-400 to-orange-500 transition-all duration-1000 ease-linear"
             style={{ width: `${((currentSlide + 1) / slides.length) * 100}%` }} />
      </div>
    </div>
  )
}