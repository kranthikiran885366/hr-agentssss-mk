"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import {
  Users,
  UserCheck,
  Clock,
  TrendingUp,
  MessageSquare,
  Phone,
  Mail,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Activity,
} from "lucide-react"
import { InterviewDashboard } from "./InterviewDashboard"
import { OnboardingDashboard } from "./OnboardingDashboard"
import { PerformanceDashboard } from "./PerformanceDashboard"
import { CommunicationDashboard } from "./CommunicationDashboard"
import { AnalyticsDashboard } from "./AnalyticsDashboard"

interface DashboardStats {
  totalCandidates: number
  activeInterviews: number
  pendingOnboarding: number
  completedHires: number
  communicationsSent: number
  averageHireTime: number
  conversionRate: number
  systemHealth: string
}

interface RecentActivity {
  id: string
  type: "interview" | "onboarding" | "communication" | "performance"
  title: string
  description: string
  timestamp: string
  status: "success" | "pending" | "failed"
  priority: "low" | "medium" | "high"
}

export function HRDashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalCandidates: 0,
    activeInterviews: 0,
    pendingOnboarding: 0,
    completedHires: 0,
    communicationsSent: 0,
    averageHireTime: 0,
    conversionRate: 0,
    systemHealth: 'good'
  })
  
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, activityResponse] = await Promise.all([
        fetch('/api/dashboard/stats'),
        fetch('/api/dashboard/activity')
      ])
      
      const statsData = await statsResponse.json()
      const activityData = await activityResponse.json()
      
      setStats(statsData)
      setRecentActivity(activityData)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Activity className="h-4 w-4 text-gray-600" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">HR Agent Dashboard</h1>
          <p className="text-gray-600">Fully automated HR operations and analytics</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={fetchDashboardData}>
            <Activity className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <BarChart3 className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* System Health Alert */}
      {stats.systemHealth !== 'good' && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-orange-800 font-medium">
                System Health: {stats.systemHealth}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="interviews">Interviews</TabsTrigger>
          <TabsTrigger value="onboarding">Onboarding</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="communication">Communication</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Candidates</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalCandidates}</div>
                <p className="text-xs text-muted-foreground">
                  +12% from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Interviews</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.activeInterviews}</div>
                <p className="text-xs text-muted-foreground">
                  AI-powered interviews
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Onboarding</CardTitle>
                <UserCheck className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.pendingOnboarding}</div>
                <p className="text-xs text-muted-foreground">
                  Automated process
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.conversionRate}%</div>
                <p className="text-xs text-muted-foreground">
                  Interview to hire
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Communication Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Communication Volume</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Mail className="h-4 w-4 text-blue-600" />
                      <span className="text-sm">Emails Sent</span>
                    </div>
                    <span className="font-semibold">{Math.floor(stats.communicationsSent * 0.6)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Phone className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Calls Made</span>
                    </div>
                    <span className="font-semibold">{Math.floor(stats.communicationsSent * 0.3)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="h-4 w-4 text-purple-600" />
                      <span className="text-sm">SMS Sent</span>
                    </div>
                    <span className="font-semibold">{Math.floor(stats.communicationsSent * 0.1)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Process Efficiency</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Average Hire Time</span>
                      <span>{stats.averageHireTime} days</span>
                    </div>
                    <Progress value={Math.max(0, 100 - (stats.averageHireTime / 30) * 100)} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Automation Rate</span>
                      <span>95%</span>
                    </div>
                    <Progress value={95} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Response Time</span>\
                      <span>< 1 hour</span>
                    </div>
                    <Progress value={90} />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">AI Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">98.5%</div>
                    <p className="text-sm text-gray-600">Overall Accuracy</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Resume Parsing</span>
                      <span className="text-green-600">99.2%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Interview Analysis</span>
                      <span className="text-green-600">97.8%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Document Verification</span>
                      <span className="text-green-600">98.5%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recent Activity</CardTitle>
              <p className="text-sm text-gray-600">Real-time HR agent operations</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                    <div className="flex-shrink-0 mt-1">
                      {getStatusIcon(activity.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {activity.title}
                        </h4>
                        <div className="flex items-center space-x-2">
                          <Badge className={getPriorityColor(activity.priority)}>
                            {activity.priority}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {new Date(activity.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interviews">
          <InterviewDashboard />
        </TabsContent>

        <TabsContent value="onboarding">
          <OnboardingDashboard />
        </TabsContent>

        <TabsContent value="performance">
          <PerformanceDashboard />
        </TabsContent>

        <TabsContent value="communication">
          <CommunicationDashboard />
        </TabsContent>

        <TabsContent value="analytics">
          <AnalyticsDashboard />
        </TabsContent>
      </Tabs>
    </div>
  )
}
