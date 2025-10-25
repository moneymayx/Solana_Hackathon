import { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'bordered'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

/**
 * Card Component
 * Reusable card container for stats, content, and more
 */
export function Card({
  className,
  variant = 'default',
  padding = 'md',
  children,
  ...props
}: CardProps) {
  const variants = {
    default: 'bg-slate-800 border border-slate-700',
    elevated: 'bg-slate-800 border border-slate-700 shadow-lg',
    bordered: 'bg-transparent border border-slate-600'
  }
  
  const paddings = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }
  
  return (
    <div
      className={cn(
        'rounded-xl transition-all duration-200',
        variants[variant],
        paddings[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  trend?: {
    value: string
    positive?: boolean
  }
  className?: string
}

/**
 * StatCard Component
 * Specialized card for displaying statistics
 */
export function StatCard({ icon, label, value, trend, className }: StatCardProps) {
  return (
    <Card variant="elevated" className={cn('relative overflow-hidden', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-slate-400 text-sm font-medium mb-1">{label}</p>
          <p className="text-slate-50 text-3xl font-bold">{value}</p>
          {trend && (
            <p
              className={cn(
                'text-sm font-medium mt-2',
                trend.positive ? 'text-emerald-400' : 'text-red-400'
              )}
            >
              {trend.value}
            </p>
          )}
        </div>
        <div className="text-4xl opacity-80">{icon}</div>
      </div>
    </Card>
  )
}

