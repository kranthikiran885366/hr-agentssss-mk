"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Users, X, CheckCircle, Clock, Shield, Mail, Settings, User } from "lucide-react"

interface OnboardingDemoProps {
  onClose: () => void
}

interface OnboardingStep {
  id: string
  title: string
  description: string
  status: "pending" | "in-progress" | "completed" | "failed"
  duration: string
  details: string[]
}

export function OnboardingDemo({ onClose }: OnboardingDemoProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isRunning, setIsRunning] = useState(false)

  const [steps, setSteps] = useState<OnboardingStep[]>([
    {
      id: "welcome",
      title: "Welcome Email",
      description: "Send personalized welcome email to new hire",
      status: "pending",
      duration: "30s",
      details: [
        "Generate personalized welcome message",
        "Include company handbook and policies",
        "Send calendar invites for first week",
        "Provide IT setup instructions",
      ],
    },
    {
      id: "documents",
      title: "Document Collection",
      description: "Collect and verify required documents",
      status: "pending",
      duration: "2-3 min",
      details: [
        "Request ID verification documents",
        "Collect tax forms and banking info",
        "AI-powered document verification",
        "Store securely in HR system",
      ],
    },
    {
      id: "accounts",
      title: "Account Creation",
      description: "Create accounts across all company systems",
      status: "pending",
      duration: "1-2 min",
      details: [
        "Google Workspace account",
        "Slack workspace access",
        "HR management system",
        "Development tools and repositories",
      ],
    },
    {
      id: "mentor",
      title: "Mentor Assignment",
      description: "AI-powered mentor matching and introduction",
      status: "pending",
      duration: "1 min",
      details: [
        "Analyze new hire profile",
        "Match with suitable mentor",
        "Send introduction email",
        "Schedule first meeting",
      ],
    },
    {
      id: "training",
      title: "Training Modules",
      description: "Assign relevant training and compliance modules",
      status: "pending",
      duration: "30s",
      details: [
        "Compliance and safety training",
        "Company culture modules",
        "Role-specific training",
        "Track completion progress",
      ],
    },
    {
      id: "completion",
      title: "Onboarding Complete",
      description: "Final setup and welcome package delivery",
      status: "pending",
      duration: "1 min",
      details: [
        "Send completion notification",
        "Schedule welcome package delivery",
        "Set up 30-day check-in",
        "Generate onboarding report",
      ],
    },
  ])

  const startOnboarding = async () => {
    setIsRunning(true)

    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i)

      // Update step to in-progress
      setSteps((prev) => prev.map((step, index) => (index === i ? { ...step, status: "in-progress" } : step)))

      // Simulate processing time
      const duration = [3000, 5000, 4000, 2000, 2000, 3000][i]
      await new Promise((resolve) => setTimeout(resolve, duration))

      // Update step to completed
      setSteps((prev) => prev.map((step, index) => (index === i ? { ...step, status: "completed" } : step)))
    }

    setIsRunning(false)
  }

  const resetDemo = () => {
    setCurrentStep(0)
    setIsRunning(false)
    setSteps((prev) => prev.map((step) => ({ ...step, status: "pending" })))
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case "in-progress":
        return <Clock className="h-5 w-5 text-blue-600 animate-spin" />
      case "failed":
        return <X className="h-5 w-5 text-red-600" />
      default:
        return <div className="w-5 h-5 border-2 border-gray-300 rounded-full" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>
      case "in-progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  const completedSteps = steps.filter((step) => step.status === "completed").length
  const progress = (completedSteps / steps.length) * 100

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <Users className="h-6 w-6 text-indigo-600" />
          <h2 className="text-2xl font-bold">Smart Onboarding Demo</h2>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Progress Overview */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Onboarding Progress</CardTitle>
          <p className="text-gray-600">Automated end-to-end onboarding for new hire: John Doe</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Overall Progress</span>
              <span className="text-sm text-gray-600">
                {completedSteps} of {steps.length} steps completed
              </span>
            </div>
            <Progress value={progress} className="w-full" />

            <div className="flex justify-center space-x-4">
              {!isRunning && completedSteps === 0 && (
                <Button onClick={startOnboarding} className="bg-indigo-600 hover:bg-indigo-700">
                  <Users className="h-4 w-4 mr-2" />
                  Start Onboarding
                </Button>
              )}

              {!isRunning && completedSteps > 0 && (
                <Button onClick={resetDemo} variant="outline">
                  Reset Demo
                </Button>
              )}

              {isRunning && (
                <Button disabled className="bg-blue-600">
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Onboarding Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <Card
            key={step.id}
            className={`transition-all duration-300 ${
              index === currentStep && isRunning ? "ring-2 ring-blue-500 shadow-lg" : ""
            }`}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-4">
                  <div className="mt-1">{getStatusIcon(step.status)}</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{step.title}</h3>
                    <p className="text-gray-600 mb-2">{step.description}</p>
                    <div className="flex items-center space-x-2">
                      {getStatusBadge(step.status)}
                      <Badge variant="outline" className="text-xs">
                        ~{step.duration}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-indigo-600">{index + 1}</span>
                  </div>
                </div>
              </div>

              {/* Step Details */}
              <div className="ml-9">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {step.details.map((detail, detailIndex) => (
                    <div
                      key={detailIndex}
                      className={`flex items-center space-x-2 text-sm p-2 rounded ${
                        step.status === "completed"
                          ? "bg-green-50 text-green-700"
                          : step.status === "in-progress"
                            ? "bg-blue-50 text-blue-700"
                            : "text-gray-600"
                      }`}
                    >
                      {step.status === "completed" ? (
                        <CheckCircle className="h-3 w-3 text-green-600" />
                      ) : step.status === "in-progress" ? (
                        <Clock className="h-3 w-3 text-blue-600" />
                      ) : (
                        <div className="w-3 h-3 border border-gray-300 rounded-full" />
                      )}
                      <span>{detail}</span>
                    </div>
                  ))}
                </div>

                {step.status === "in-progress" && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-blue-600 animate-spin" />
                      <span className="text-sm text-blue-700">Processing {step.title.toLowerCase()}...</span>
                    </div>
                  </div>
                )}

                {step.status === "completed" && (
                  <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm text-green-700">{step.title} completed successfully</span>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Completion Summary */}
      {completedSteps === steps.length && !isRunning && (
        <Card className="mt-6 border-green-200 bg-green-50">
          <CardContent className="p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-green-900 mb-2">Onboarding Complete!</h3>
            <p className="text-green-700 mb-4">
              John Doe has been successfully onboarded. All systems are set up and ready.
            </p>
            <div className="flex justify-center space-x-4">
              <Button className="bg-green-600 hover:bg-green-700">View Onboarding Report</Button>
              <Button variant="outline">Schedule 30-Day Check-in</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Automation Features */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Automation Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              {
                icon: Mail,
                title: "Email Automation",
                description: "Personalized emails at each step",
              },
              {
                icon: Shield,
                title: "Document Verification",
                description: "AI-powered identity verification",
              },
              {
                icon: Settings,
                title: "System Integration",
                description: "Automatic account provisioning",
              },
              {
                icon: User,
                title: "Mentor Matching",
                description: "AI-based mentor assignment",
              },
            ].map((feature, index) => (
              <div key={index} className="text-center p-4 border rounded-lg">
                <feature.icon className="h-8 w-8 text-indigo-600 mx-auto mb-2" />
                <h4 className="font-medium mb-1">{feature.title}</h4>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
