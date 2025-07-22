"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Clock, Settings, Mail, Shield, Database } from "lucide-react"

interface AccountCreationStepProps {
  onNext: () => void
  onPrevious: () => void
}

interface AccountService {
  name: string
  description: string
  status: "pending" | "creating" | "completed" | "failed"
  icon: React.ElementType
  credentials?: {
    username?: string
    email?: string
    tempPassword?: string
  }
}

export function AccountCreationStep({ onNext, onPrevious }: AccountCreationStepProps) {
  const [services, setServices] = useState<AccountService[]>([
    {
      name: "Google Workspace",
      description: "Email, Drive, Calendar, and collaboration tools",
      status: "pending",
      icon: Mail,
    },
    {
      name: "HR Management System",
      description: "Employee portal and HR services",
      status: "pending",
      icon: Database,
    },
    {
      name: "Security Access",
      description: "Building access and security credentials",
      status: "pending",
      icon: Shield,
    },
    {
      name: "Development Tools",
      description: "Code repositories and development environment",
      status: "pending",
      icon: Settings,
    },
  ])

  const [currentlyCreating, setCurrentlyCreating] = useState(-1)
  const [allComplete, setAllComplete] = useState(false)

  useEffect(() => {
    const createAccounts = async () => {
      for (let i = 0; i < services.length; i++) {
        setCurrentlyCreating(i)

        // Update status to creating
        setServices((prev) =>
          prev.map((service, index) => (index === i ? { ...service, status: "creating" } : service)),
        )

        // Simulate account creation time
        await new Promise((resolve) => setTimeout(resolve, 3000))

        // Simulate account creation result
        const isSuccessful = Math.random() > 0.05 // 95% success rate

        setServices((prev) =>
          prev.map((service, index) =>
            index === i
              ? {
                  ...service,
                  status: isSuccessful ? "completed" : "failed",
                  credentials: isSuccessful
                    ? {
                        username: `john.doe${i + 1}`,
                        email: `john.doe@company.com`,
                        tempPassword: "TempPass123!",
                      }
                    : undefined,
                }
              : service,
          ),
        )
      }

      setAllComplete(true)
    }

    const timer = setTimeout(createAccounts, 1000)
    return () => clearTimeout(timer)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case "failed":
        return <CheckCircle className="h-5 w-5 text-red-600" />
      case "creating":
        return <Clock className="h-5 w-5 text-blue-600 animate-spin" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800">Created</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      case "creating":
        return <Badge className="bg-blue-100 text-blue-800">Creating...</Badge>
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  const completedCount = services.filter((s) => s.status === "completed").length
  const canProceed = allComplete && completedCount >= 3

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-6 w-6 text-blue-600" />
            <span>Account Creation</span>
          </CardTitle>
          <p className="text-gray-600">We're automatically creating your accounts across all company systems.</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {services.map((service, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <service.icon className="h-6 w-6 text-gray-600" />
                    <div>
                      <h3 className="font-medium">{service.name}</h3>
                      <p className="text-sm text-gray-600">{service.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(service.status)}
                    {getStatusBadge(service.status)}
                  </div>
                </div>

                {service.status === "creating" && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                    <p className="text-sm text-blue-700">Creating your {service.name} account...</p>
                  </div>
                )}

                {service.status === "completed" && service.credentials && (
                  <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded">
                    <h4 className="font-medium text-green-900 mb-2">Account Created Successfully</h4>
                    <div className="text-sm text-green-700 space-y-1">
                      {service.credentials.email && (
                        <p>
                          <strong>Email:</strong> {service.credentials.email}
                        </p>
                      )}
                      {service.credentials.username && (
                        <p>
                          <strong>Username:</strong> {service.credentials.username}
                        </p>
                      )}
                      {service.credentials.tempPassword && (
                        <p>
                          <strong>Temporary Password:</strong> {service.credentials.tempPassword}
                        </p>
                      )}
                    </div>
                    <p className="text-xs text-green-600 mt-2">You'll receive detailed login instructions via email.</p>
                  </div>
                )}

                {service.status === "failed" && (
                  <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
                    <p className="text-sm text-red-700">
                      Failed to create {service.name} account. Our IT team has been notified.
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {allComplete && (
            <div className="mt-6 p-4 bg-gray-50 border rounded-lg">
              <h3 className="font-medium mb-2">Account Creation Summary</h3>
              <div className="text-sm space-y-2">
                <p>
                  <span className="text-gray-600">Successfully Created:</span>
                  <span className="ml-2 font-medium text-green-600">{completedCount} accounts</span>
                </p>
                <p className="text-gray-600">
                  You'll receive welcome emails with detailed setup instructions for each service. Please check your
                  personal email within the next 24 hours.
                </p>
                {canProceed && (
                  <p className="text-green-600 font-medium">
                    ✓ Account setup complete! Ready to proceed to mentor assignment.
                  </p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={onNext} disabled={!canProceed}>
          {canProceed ? "Continue to Mentor Assignment" : "Creating Accounts..."}
        </Button>
      </div>
    </div>
  )
}
