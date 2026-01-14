import * as React from 'react'
import { cn } from '../../lib/utils'

const Textarea = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        'flex min-h-[44px] w-full rounded-2xl border border-black/15 bg-white/70 px-4 py-3 text-sm shadow-sm outline-none transition focus:border-black focus:ring-2 focus:ring-black focus:ring-offset-2 focus:ring-offset-white placeholder:text-neutral-500 disabled:cursor-not-allowed disabled:opacity-60',
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = 'Textarea'

export { Textarea }
