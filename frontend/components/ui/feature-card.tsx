"use client"

import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
  className?: string
}

export function FeatureCard({
  icon: Icon,
  title,
  description,
  className,
}: FeatureCardProps) {
  return (
    <div className={cn(
      "relative overflow-hidden rounded-lg border bg-card p-6",
      "hover:shadow-lg transition-all duration-300",
      "group",
      className
    )}>
      <div className="relative z-10">
        <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
          <Icon className="h-6 w-6 text-primary" />
        </div>
        <h3 className="mb-2 text-lg font-semibold">
          {title}
        </h3>
        <p className="text-muted-foreground">
          {description}
        </p>
      </div>
      <div className="absolute inset-0 z-0 bg-gradient-to-br from-primary/5 to-background opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    </div>
  )
}
