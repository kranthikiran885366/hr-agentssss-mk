"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Calendar, Mail, BookOpen, Users, Gift, ArrowRight } from "lucide-react"
import Link from "next/link"
import type { User } from "@/types/user"

interface CompletionStepProps {
  user: User
}

export function CompletionStep({ user }: CompletionStepProps) {
  const completedTasks = [
    { title: "Document Upload", description: "All required documents uploaded successfully" },
    { title: "Identity Verification", description: "Documents verified with 95% confidence" },
    { title: "Account Creation", description: "4 system accounts created and configured" },
    { title: "Mentor Assignment", description: "Matched with experienced mentor" },
  ]

  const nextSteps = [
    {
      icon: Calendar,
      title: "First Day Orientation",
      description: "Join the company-wide orientation session",
      action: "View Schedule",
      urgent: true,
    },
    {
      icon: Mail,
      title: "Check Your Email",
      description: "Important setup instructions and welcome materials",
      action: "Open Email",
      urgent: true,
    },
    {
      icon: BookOpen,
      title: "Complete Training Modules",
      description: "Start with mandatory compliance and safety training",
      action: "Start Training",
      urgent: false,
    },
    {
      icon: Users,
      title: "Meet Your Team",
      description: "Schedule introductory meetings with team members",
      action: "View Team",
      urgent: false,
    },
  ]

  const welcomePackage = [
    "Company handbook and policies",
    "Employee benefits guide",
    "IT equipment and setup instructions",
    "Office access cards and parking pass",
    "Welcome gift package",
    "First week schedule and calendar invites",
  ]

  return (
    <div className="space-y-6">
      <Card className="border-green-200 bg-green-50">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-2xl text-green-900">Welcome to the Team, {user.name}!</CardTitle>
          <p className="text-green-700">
            Your onboarding process is now complete. We're excited to have you join our company!
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {completedTasks.map((task, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-green-200">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <div>
                  <h3 className="font-medium text-gray-900">{task.title}</h3>
                  <p className="text-sm text-gray-600">{task.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <ArrowRight className="h-6 w-6 text-blue-600" />
            <span>Next Steps</span>
          </CardTitle>
          <p className="text-gray-600">Here's what you need to do to get started in your new role.</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {nextSteps.map((step, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <step.icon className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium">{step.title}</h3>
                      {step.urgent && (
                        <Badge variant="destructive" className="text-xs">
                          Urgent
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{step.description}</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  {step.action}
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Gift className="h-6 w-6 text-purple-600" />
              <span>Welcome Package</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Your welcome package will be delivered to your address within 2-3 business days:
            </p>
            <ul className="space-y-2">
              {welcomePackage.map((item, index) => (
                <li key={index} className="flex items-center space-x-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Important Contacts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <h4 className="font-medium">HR Support</h4>
              <p className="text-sm text-gray-600">hr-support@company.com</p>
              <p className="text-sm text-gray-600">+1 (555) 123-4567</p>
            </div>
            <div>
              <h4 className="font-medium">IT Helpdesk</h4>
              <p className="text-sm text-gray-600">it-help@company.com</p>
              <p className="text-sm text-gray-600">+1 (555) 123-4568</p>
            </div>
            <div>
              <h4 className="font-medium">Your Manager</h4>
              <p className="text-sm text-gray-600">manager@company.com</p>
              <p className="text-sm text-gray-600">Available for questions</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="text-center space-y-4">
        <p className="text-gray-600">
          Ready to start your journey with us? Access your dashboard to explore your new workspace.
        </p>
        <div className="space-x-4">
          <Link href="/dashboard">
            <Button size="lg">Go to Dashboard</Button>
          </Link>
          <Button variant="outline" size="lg">
            Download Mobile App
          </Button>
        </div>
      </div>
    </div>
  )
}
