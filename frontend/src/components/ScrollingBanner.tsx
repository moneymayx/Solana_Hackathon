'use client'

import { useState, useEffect } from 'react'
import { Download, Users, Gift, Star, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ScrollingBannerProps {
  className?: string
}

export default function ScrollingBanner({ className }: ScrollingBannerProps) {
  const [currentSlide, setCurrentSlide] = useState(0)

  // Only the two banner images
  const slides = [
    {
      id: 1,
      type: 'jackpot',
      title: 'Claude Champ',
      subtitle: 'Beat the Bot',
      description: 'Think you can outsmart the most advanced AI?',
      prize: '$50,000',
      image: '/images/claude-champion-banner.jpg',
      bgGradient: 'from-yellow-400 via-orange-500 to-red-500',
      textColor: 'text-slate-900',
      isBannerImage: true
    },
    {
      id: 2,
      type: 'download',
      title: 'Download the Billions App',
      subtitle: 'Play Anywhere',
      description: 'Take the challenge with you wherever you go',
      prize: 'Mobile Ready',
      image: '/images/billions-app-banner.JPEG',
      bgGradient: 'from-green-400 via-emerald-500 to-teal-500',
      textColor: 'text-white',
      isBannerImage: true
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
      <div className="relative bg-gradient-to-r from-slate-800 to-slate-900 overflow-hidden">
        {/* Background Image - only for non-banner slides */}
        {!currentSlideData.isBannerImage && (
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
        )}
        
        {/* Slide Content */}
        <div className="relative">
          {currentSlideData.isBannerImage ? (
            // Full banner image with auto-sizing to show complete image
            <div className="w-full bg-gray-100">
              <img
                src={currentSlideData.image}
                alt={currentSlideData.title}
                className="w-full h-auto max-h-[600px] object-contain mx-auto block"
                onError={(e) => {
                  console.log('Image failed to load:', currentSlideData.image)
                  // Fallback to gradient circle with emoji
                  e.currentTarget.style.display = 'none'
                  const fallback = e.currentTarget.nextElementSibling as HTMLElement
                  if (fallback) fallback.style.display = 'flex'
                }}
                onLoad={() => {
                  console.log('Image loaded successfully:', currentSlideData.image)
                }}
              />
              {/* Fallback placeholder */}
              <div className="w-full h-64 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-gray-500 text-lg hidden">
                Image not available
              </div>
            </div>
          ) : (
            <div className="flex flex-col md:flex-row items-center justify-between p-6 md:p-8 min-h-[300px] md:min-h-[400px]">
              <>
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
              </>
            </div>
          )}
        </div>

        {/* Slide Indicators - only show for non-banner slides */}
        {!currentSlideData.isBannerImage && (
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
        )}

        {/* Progress Bar - only show for non-banner slides */}
        {!currentSlideData.isBannerImage && (
          <div className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-yellow-400 to-orange-500 transition-all duration-1000 ease-linear"
               style={{ width: `${((currentSlide + 1) / slides.length) * 100}%` }} />
        )}
      </div>
    </div>
  )
}