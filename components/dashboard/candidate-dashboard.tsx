"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileText, CheckCircle, Clock, AlertCircle, BookOpen } from "lucide-react"
import Link from "next/link"
import type { User } from "@/types/user"

interface CandidateDashboardProps {
  user: User
}

export function CandidateDashboard({ user }: CandidateDashboardProps) {
  const onboardingProgress = 75 // This would come from API

  const tasks = [
    { id: 1, title: "Upload Documents", status: "completed", icon: FileText },
    { id: 2, title: "Document Verification", status: "in-progress", icon: CheckCircle },
    { id: 3, title: "Account Creation", status: "pending", icon: BookOpen },
    { id: 4, title: "Mentor Assignment", status: "pending", icon: BookOpen },
    { id: 5, title: "Module Assignment", status: "pending", icon: BookOpen },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case "in-progress":
        return <Clock className="h-5 w-5 text-yellow-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <Badge variant="default" className="bg-green-100 text-green-800">
            Completed
          </Badge>
        )
      case "in-progress":
        return (
          <Badge variant="default" className="bg-yellow-100 text-yellow-800">
            In Progress
          </Badge>
        )
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome, {user.name}!</h1>
        <p className="text-gray-600">Track your onboarding progress and complete required tasks.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Onboarding Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress value={onboardingProgress} className="w-full" />
              <p className="text-sm text-gray-600">{onboardingProgress}% Complete</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Documents Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm">2 of 3 verified</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Next Action</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm font-medium">Document Verification</p>
              <p className="text-xs text-gray-600">Waiting for admin review</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Onboarding Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(task.status)}
                  <div>
                    <h3 className="font-medium">{task.title}</h3>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusBadge(task.status)}
                  {task.status === "in-progress" && (
                    <Button size="sm" variant="outline">
                      View Details
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex space-x-4">
        <Link href="/onboarding">
          <Button>Continue Onboarding</Button>
        </Link>
        <Button variant="outline">View Documents</Button>
      </div>
    </div>
  )
}
