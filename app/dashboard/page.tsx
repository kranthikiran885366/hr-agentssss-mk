"use client"

import { useState, useEffect } from "react"
import { HRDashboard } from "@/components/hr-dashboard/HRDashboard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import {
  Users,
  Bot,
  MessageSquare,
  Video,
  Calendar,
  FileText,
  Shield,
  Zap,
  CheckCircle,
  TrendingUp,
  Activity,
  RefreshCw,
} from "lucide-react"
import { RequisitionApproval } from "@/components/talent-acquisition/requisition-approval"
import { DiversityReport } from "@/components/talent-acquisition/diversity-report"
import { CandidatePipeline } from "@/components/talent-acquisition/candidate-pipeline"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { NotificationCenter } from "./NotificationCenter"
import { AuditLogViewer } from "./AuditLogViewer"
import { CandidateProfile } from "@/components/talent-acquisition/CandidateProfile"

interface DashboardMetrics {
  totalEmployees: number
  activeProcesses: number
  automationRate: number
  systemHealth: string
  todayStats: {
    interviews: number
    onboarding: number
    leaves: number
    communications: number
  }
  weeklyTrends: {
    hiring: number
    performance: number
    engagement: number
    efficiency: number
  }
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalEmployees: 2847,
    activeProcesses: 156,
    automationRate: 98.7,
    systemHealth: "excellent",
    todayStats: {
      interviews: 23,
      onboarding: 8,
      leaves: 45,
      communications: 342,
    },
    weeklyTrends: {
      hiring: 15.2,
      performance: 8.7,
      engagement: 12.4,
      efficiency: 22.1,
    },
  })

  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [activeTab, setActiveTab] = useState("overview")
  const jobOptions = [
    { id: "job-1", title: "Senior Software Engineer" },
    { id: "job-2", title: "Product Manager" },
  ] // TODO: Fetch real jobs for DiversityReport
  const [profileCandidateId, setProfileCandidateId] = useState<string | null>(null)

  useEffect(() => {
    // Simulate real-time data loading
    const timer = setTimeout(() => {
      setLoading(false)
    }, 1500)

    // Set up real-time updates
    const updateInterval = setInterval(() => {
      setLastUpdated(new Date())
      // Simulate small changes in metrics
      setMetrics((prev) => ({
        ...prev,
        activeProcesses: prev.activeProcesses + Math.floor(Math.random() * 5) - 2,
        todayStats: {
          ...prev.todayStats,
          communications: prev.todayStats.communications + Math.floor(Math.random() * 3),
        },
      }))
    }, 30000) // Update every 30 seconds

    return () => {
      clearTimeout(timer)
      clearInterval(updateInterval)
    }
  }, [])

  const refreshData = async () => {
    setLoading(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setLastUpdated(new Date())
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600">Loading HR Dashboard...</p>
          <p className="text-sm text-gray-500">Initializing all 150+ HR functions</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">HR Command Center</h1>
            <p className="text-gray-600">Complete automation dashboard with 150+ active functions</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">Last updated</p>
              <p className="text-sm font-medium">{lastUpdated.toLocaleTimeString()}</p>
            </div>
            <Button onClick={refreshData} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Badge
              variant={metrics.systemHealth === "excellent" ? "default" : "destructive"}
              className={metrics.systemHealth === "excellent" ? "bg-green-100 text-green-800" : ""}
            >
              <Activity className="h-3 w-3 mr-1" />
              {metrics.systemHealth.toUpperCase()}
            </Badge>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{metrics.totalEmployees.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Across all departments</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Processes</CardTitle>
              <Bot className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{metrics.activeProcesses}</div>
              <p className="text-xs text-muted-foreground">Running automatically</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Automation Rate</CardTitle>
              <Zap className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{metrics.automationRate}%</div>
              <p className="text-xs text-muted-foreground">Fully automated</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Shield className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600 capitalize">{metrics.systemHealth}</div>
              <p className="text-xs text-muted-foreground">All systems operational</p>
            </CardContent>
          </Card>
        </div>

        {/* Today's Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-blue-600" />
                <span>Today's Activity</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Video className="h-4 w-4 text-blue-600" />
                    <span className="text-sm">AI Interviews Conducted</span>
                  </div>
                  <Badge variant="secondary">{metrics.todayStats.interviews}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-green-600" />
                    <span className="text-sm">Onboarding Processes</span>
                  </div>
                  <Badge variant="secondary">{metrics.todayStats.onboarding}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm">Leave Applications</span>
                  </div>
                  <Badge variant="secondary">{metrics.todayStats.leaves}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="h-4 w-4 text-purple-600" />
                    <span className="text-sm">Automated Communications</span>
                  </div>
                  <Badge variant="secondary">{metrics.todayStats.communications}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                <span>Weekly Trends</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Hiring Efficiency</span>
                    <span className="text-green-600">+{metrics.weeklyTrends.hiring}%</span>
                  </div>
                  <Progress value={metrics.weeklyTrends.hiring + 60} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Performance Reviews</span>
                    <span className="text-blue-600">+{metrics.weeklyTrends.performance}%</span>
                  </div>
                  <Progress value={metrics.weeklyTrends.performance + 70} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Employee Engagement</span>
                    <span className="text-purple-600">+{metrics.weeklyTrends.engagement}%</span>
                  </div>
                  <Progress value={metrics.weeklyTrends.engagement + 65} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Process Efficiency</span>
                    <span className="text-yellow-600">+{metrics.weeklyTrends.efficiency}%</span>
                  </div>
                  <Progress value={metrics.weeklyTrends.efficiency + 55} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Dashboard Component */}
        <Tabs defaultValue="overview" value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="pipeline">Candidate Pipeline</TabsTrigger>
            <TabsTrigger value="requisitions">Requisition Approval</TabsTrigger>
            <TabsTrigger value="diversity">Diversity Report</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          </TabsList>
          <TabsContent value="overview">
            <HRDashboard />
          </TabsContent>
          <TabsContent value="pipeline">
            <CandidatePipeline onProfileOpen={setProfileCandidateId} />
          </TabsContent>
          <TabsContent value="requisitions">
            <RequisitionApproval />
          </TabsContent>
          <TabsContent value="diversity">
            <DiversityReport jobOptions={jobOptions} />
          </TabsContent>
          <TabsContent value="notifications">
            <NotificationCenter />
          </TabsContent>
          <TabsContent value="audit">
            <AuditLogViewer />
          </TabsContent>
        </Tabs>

        {profileCandidateId && (
          <CandidateProfile candidateId={profileCandidateId} onClose={() => setProfileCandidateId(null)} />
        )}

        {/* System Status */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-green-600" />
              <span>System Status - All 150+ Functions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {[
                { name: "Talent Acquisition", status: "operational", count: 15 },
                { name: "Onboarding", status: "operational", count: 12 },
                { name: "Attendance", status: "operational", count: 18 },
                { name: "Performance", status: "operational", count: 14 },
                { name: "Payroll", status: "operational", count: 16 },
                { name: "Learning", status: "operational", count: 13 },
                { name: "Compliance", status: "operational", count: 11 },
                { name: "Communication", status: "operational", count: 19 },
                { name: "Exit Management", status: "operational", count: 9 },
                { name: "Analytics", status: "operational", count: 12 },
                { name: "AI Automation", status: "operational", count: 8 },
                { name: "Security", status: "operational", count: 3 },
              ].map((system, index) => (
                <div key={index} className="text-center p-3 border rounded-lg">
                  <div className="flex items-center justify-center mb-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  <h4 className="font-medium text-sm text-gray-900">{system.name}</h4>
                  <p className="text-xs text-gray-500">{system.count} functions</p>
                  <Badge variant="secondary" className="mt-1 text-xs bg-green-100 text-green-800">
                    {system.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
