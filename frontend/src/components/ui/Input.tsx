import { InputHTMLAttributes, forwardRef, TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string
  fullWidth?: boolean
}

/**
 * Input Component
 * Reusable text input following the new design system
 */
const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, fullWidth = false, ...props }, ref) => {
    return (
      <div className={cn('flex flex-col gap-1', fullWidth && 'w-full')}>
        <input
          ref={ref}
          className={cn(
            'bg-slate-700 text-slate-50 placeholder-slate-400',
            'px-4 py-2 rounded-lg',
            'border border-slate-600',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'transition-all duration-200',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error && 'border-red-500 focus:ring-red-500',
            className
          )}
          {...props}
        />
        {error && <span className="text-red-400 text-sm">{error}</span>}
      </div>
    )
  }
)

Input.displayName = 'Input'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string
  fullWidth?: boolean
}

/**
 * Textarea Component
 * Reusable textarea following the new design system
 */
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, fullWidth = false, ...props }, ref) => {
    return (
      <div className={cn('flex flex-col gap-1', fullWidth && 'w-full')}>
        <textarea
          ref={ref}
          className={cn(
            'bg-slate-700 text-slate-50 placeholder-slate-400',
            'px-4 py-2 rounded-lg',
            'border border-slate-600',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'transition-all duration-200',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'resize-none',
            error && 'border-red-500 focus:ring-red-500',
            className
          )}
          {...props}
        />
        {error && <span className="text-red-400 text-sm">{error}</span>}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

export default Input

