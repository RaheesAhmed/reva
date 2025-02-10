"use client"

import { cn } from "@/lib/utils"

interface GradientTextProps extends React.HTMLAttributes<HTMLSpanElement> {
  children: React.ReactNode
  from?: string
  to?: string
  animate?: boolean
  direction?: 'ltr' | 'rtl'
}

export function GradientText({
  children,
  from = "from-primary",
  to = "to-primary-light",
  animate = false,
  direction = 'ltr',
  className,
  ...props
}: GradientTextProps) {
  return (
    <span
      className={cn(
        "bg-gradient-to-r bg-clip-text text-transparent",
        from,
        to,
        animate && "animate-text-gradient bg-[200%_auto]",
        direction === 'rtl' && "bg-gradient-to-l",
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
}
