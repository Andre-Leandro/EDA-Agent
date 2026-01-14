import * as React from 'react'
import { cn } from '../../lib/utils'

function Card({ className, ...props }) {
  return (
    <div
      className={cn(
        'rounded-3xl border border-white/40 bg-white/30 backdrop-blur-xl shadow-xl',
        className
      )}
      {...props}
    />
  )
}

function CardContent({ className, ...props }) {
  return <div className={cn('p-4 md:p-6', className)} {...props} />
}

export { Card, CardContent }
