'use client'

import { Download, Star, Users } from 'lucide-react'

interface AppDownloadSectionProps {
  className?: string
}

export default function AppDownloadSection({ className }: AppDownloadSectionProps) {
  return (
    <section className={`py-16 px-4 sm:px-6 lg:px-8 ${className}`}>
      <div className="max-w-7xl mx-auto">
        {/* Shimmery Background */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-600 via-purple-700 to-green-600 p-8 md:p-12">
          {/* Animated background elements */}
          <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 via-transparent to-green-400/20 animate-pulse" />
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-transparent via-white/5 to-transparent" />
          
          <div className="relative z-10 text-center">
            {/* Reviews Section */}
            <div className="mb-8">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <div className="flex items-center space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <span className="text-white/90 text-lg font-medium">4.8/5</span>
              </div>
              
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Join Thousands of Winners
              </h2>
              
              <p className="text-white/80 text-lg max-w-2xl mx-auto mb-8">
                Download our app and start challenging AI models from anywhere. 
                Join the community of successful bounty hunters.
              </p>
              
              <div className="flex items-center justify-center space-x-6 text-white/70 text-sm">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>50K+ Active Users</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Download className="h-4 w-4" />
                  <span>1M+ Downloads</span>
                </div>
              </div>
            </div>

            {/* Download Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              {/* Apple App Store */}
              <a
                href="#"
                className="group flex items-center space-x-3 bg-black/20 hover:bg-black/30 backdrop-blur-sm border border-white/20 rounded-xl px-6 py-4 transition-all duration-200 hover:scale-105"
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
                className="group flex items-center space-x-3 bg-black/20 hover:bg-black/30 backdrop-blur-sm border border-white/20 rounded-xl px-6 py-4 transition-all duration-200 hover:scale-105"
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
                className="group flex items-center space-x-3 bg-black/20 hover:bg-black/30 backdrop-blur-sm border border-white/20 rounded-xl px-6 py-4 transition-all duration-200 hover:scale-105"
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

            {/* Additional Info */}
            <div className="mt-8 text-center">
              <p className="text-white/60 text-sm">
                Free to download • No subscription required • Start winning immediately
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
