"use client"

import { CheckCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface Step {
  id: number
  title: string
  description: string
}

interface StepTrackerProps {
  steps: Step[]
  currentStep: number
  completedSteps: number[]
}

export function StepTracker({ steps, currentStep, completedSteps }: StepTrackerProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors",
                  completedSteps.includes(step.id)
                    ? "bg-green-600 border-green-600 text-white"
                    : currentStep === step.id
                      ? "bg-blue-600 border-blue-600 text-white"
                      : "bg-white border-gray-300 text-gray-400",
                )}
              >
                {completedSteps.includes(step.id) ? (
                  <CheckCircle className="h-6 w-6" />
                ) : (
                  <span className="text-sm font-medium">{step.id}</span>
                )}
              </div>
              <div className="mt-2 text-center">
                <p
                  className={cn(
                    "text-sm font-medium",
                    completedSteps.includes(step.id) || currentStep === step.id ? "text-gray-900" : "text-gray-500",
                  )}
                >
                  {step.title}
                </p>
                <p className="text-xs text-gray-500 max-w-24">{step.description}</p>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div
                className={cn(
                  "flex-1 h-0.5 mx-4 transition-colors",
                  completedSteps.includes(step.id) ? "bg-green-600" : "bg-gray-300",
                )}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
