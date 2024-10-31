import React from 'react'
import { cn } from '../../lib/utils'

export const Button = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors",
        "px-4 py-2 bg-blue-500 text-white hover:bg-blue-600",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"
