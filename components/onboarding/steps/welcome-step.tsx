"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckCircle, FileText, Shield, BookOpen, Award } from "lucide-react"
import type { User } from "@/types/user"

interface WelcomeStepProps {
  user: User
  onNext: () => void
}

export function WelcomeStep({ user, onNext }: WelcomeStepProps) {
  const features = [
    {
      icon: FileText,
      title: "Document Upload",
      description: "Securely upload your identification and qualification documents",
    },
    {
      icon: Shield,
      title: "Verification Process",
      description: "AI-powered document verification for authenticity",
    },
    {
      icon: BookOpen,
      title: "Learning Modules",
      description: "Access to personalized training and development programs",
    },
    {
      icon: Award,
      title: "Mentor Assignment",
      description: "Get paired with an experienced mentor for guidance",
    },
  ]

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Welcome to Our Company, {user.name}!</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-gray-600 text-lg">
              We're excited to have you join our team. This onboarding process will help you get set up with everything
              you need to start your journey with us.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-blue-900">What to Expect</h3>
                  <p className="text-blue-700 text-sm mt-1">
                    The entire process typically takes 15-20 minutes and includes document upload, verification, and
                    account setup. You can save your progress and return anytime.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Onboarding Process Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {features.map((feature, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 border rounded-lg">
                <feature.icon className="h-6 w-6 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-medium text-gray-900">{feature.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Required Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Government-issued ID (Passport, Driver's License, or Aadhar Card)</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Educational Certificates (Degree, Diploma, or relevant qualifications)</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Resume/CV (Latest version)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={onNext} size="lg">
          Get Started
        </Button>
      </div>
    </div>
  )
}
