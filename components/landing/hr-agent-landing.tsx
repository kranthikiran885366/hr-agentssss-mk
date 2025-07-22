"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Users,
  Bot,
  MessageSquare,
  Calendar,
  FileText,
  BarChart3,
  Shield,
  CheckCircle,
  Clock,
  DollarSign,
  GraduationCap,
  Download,
} from "lucide-react"
import { safeToLowerCase } from "@/lib/utils"

interface FunctionalityCategory {
  name: string
  count: number
  icon: any
  color: string
  functions: string[]
  implemented: boolean
}

export function HRAgentLanding() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all")

  const functionalityCategories: FunctionalityCategory[] = [
    {
      name: "Talent Acquisition",
      count: 15,
      icon: Users,
      color: "blue",
      implemented: true,
      functions: [
        "Job requisition approval",
        "Job description creation",
        "Job posting automation",
        "Resume parsing & analysis",
        "AI-powered resume screening",
        "Candidate shortlisting",
        "Interview scheduling",
        "Panel coordination",
        "Pre-interview test setup",
        "AI interviewing (voice/video)",
        "Feedback collection",
        "Offer management",
        "Background verification",
        "Pre-boarding automation",
        "Candidate communication",
      ],
    },
    {
      name: "Employee Onboarding",
      count: 12,
      icon: FileText,
      color: "green",
      implemented: true,
      functions: [
        "Document upload & verification",
        "Welcome kit generation",
        "ID card creation",
        "Policy e-signing",
        "Manager/team introductions",
        "Training schedule assignment",
        "Probation tracking",
        "HR buddy assignment",
        "System access setup",
        "Workspace allocation",
        "Onboarding progress tracking",
        "Completion certification",
      ],
    },
    {
      name: "Attendance & Leave",
      count: 18,
      icon: Calendar,
      color: "yellow",
      implemented: true,
      functions: [
        "Shift planning & rotation",
        "Attendance logging (GPS/Biometric)",
        "Late/early detection",
        "Leave policy management",
        "Leave application & approval",
        "Holiday calendar sync",
        "Comp-off/LOP adjustment",
        "Attendance analytics",
        "Overtime tracking",
        "Work from home management",
        "Time tracking",
        "Break time monitoring",
        "Attendance reports",
        "Leave balance tracking",
        "Emergency leave handling",
        "Attendance violations",
        "Shift swapping",
        "Attendance forecasting",
      ],
    },
    {
      name: "Performance Management",
      count: 14,
      icon: BarChart3,
      color: "purple",
      implemented: true,
      functions: [
        "KPI/OKR setting",
        "Self-review process",
        "Manager review system",
        "360-degree feedback",
        "Final rating calculation",
        "Bell curve normalization",
        "Performance alerts",
        "PIP management",
        "Goal tracking",
        "Performance analytics",
        "Calibration sessions",
        "Performance trends",
        "Skill assessment",
        "Career development planning",
      ],
    },
    {
      name: "Payroll & Compensation",
      count: 16,
      icon: DollarSign,
      color: "red",
      implemented: true,
      functions: [
        "CTC breakdown management",
        "Salary processing",
        "Tax calculation (TDS)",
        "Payslip generation",
        "Variable pay management",
        "Incentives & bonuses",
        "Advance salary requests",
        "Reimbursements",
        "Statutory compliance",
        "Gratuity calculation",
        "Full & final settlement",
        "Salary revision",
        "Arrears calculation",
        "Loan management",
        "Investment declarations",
        "Form 16 generation",
      ],
    },
    {
      name: "Learning & Development",
      count: 13,
      icon: GraduationCap,
      color: "indigo",
      implemented: true,
      functions: [
        "Skill gap analysis",
        "LMS integration",
        "Training assignment",
        "Certification tracking",
        "Training feedback",
        "Personalized learning paths",
        "Training calendar",
        "Training effectiveness",
        "Learning analytics",
        "External training approval",
        "Training budget tracking",
        "Trainer management",
        "Course catalog management",
      ],
    },
    {
      name: "Policy & Compliance",
      count: 11,
      icon: Shield,
      color: "pink",
      implemented: true,
      functions: [
        "Digital policy library",
        "E-sign enforcement",
        "Grievance system",
        "POSH compliance",
        "Internal audits",
        "Labor law compliance",
        "GDPR/Data protection",
        "Policy acknowledgment",
        "Compliance reporting",
        "Risk assessment",
        "Audit trail management",
      ],
    },
    {
      name: "Communication & Engagement",
      count: 19,
      icon: MessageSquare,
      color: "cyan",
      implemented: true,
      functions: [
        "WhatsApp automation",
        "Email campaigns",
        "SMS notifications",
        "Voice calls (AI)",
        "Video interviews",
        "Slack integration",
        "Birthday/Anniversary alerts",
        "Announcements",
        "Surveys & polls",
        "Event management",
        "Newsletter automation",
        "Feedback collection",
        "Employee recognition",
        "Internal chat",
        "Push notifications",
        "Multi-language support",
        "Communication analytics",
        "Emergency broadcasts",
        "Social collaboration",
      ],
    },
    {
      name: "Exit Management",
      count: 9,
      icon: Clock,
      color: "orange",
      implemented: true,
      functions: [
        "Resignation workflow",
        "Exit interview scheduling",
        "Feedback collection",
        "Clearance checklist",
        "Final settlement",
        "Exit documentation",
        "Alumni portal access",
        "Knowledge transfer",
        "Asset recovery",
      ],
    },
    {
      name: "Analytics & Reporting",
      count: 12,
      icon: BarChart3,
      color: "teal",
      implemented: true,
      functions: [
        "Attrition reports",
        "Headcount analytics",
        "Diversity & inclusion stats",
        "Hiring funnel analysis",
        "Payroll cost analysis",
        "Training ROI",
        "Custom report builder",
        "Real-time dashboards",
        "Predictive analytics",
        "Benchmark reports",
        "Executive summaries",
        "Compliance reports",
      ],
    },
    {
      name: "AI & Automation",
      count: 8,
      icon: Bot,
      color: "violet",
      implemented: true,
      functions: [
        "AI resume screening",
        "Automated interviews",
        "Chatbot assistance",
        "Workflow automation",
        "Predictive analytics",
        "Sentiment analysis",
        "Auto-decision making",
        "Process optimization",
      ],
    },
    {
      name: "Security & Access",
      count: 3,
      icon: Download,
      color: "gray",
      implemented: true,
      functions: ["Role-based access control", "Multi-factor authentication", "Audit logging"],
    },
  ]

  const totalFunctions = functionalityCategories.reduce((sum, cat) => sum + cat.count, 0)
  const implementedFunctions = functionalityCategories
    .filter((cat) => cat.implemented)
    .reduce((sum, cat) => sum + cat.count, 0)

  const filteredCategories =
    selectedCategory === "all"
      ? functionalityCategories
      : functionalityCategories.filter((cat) => safeToLowerCase(cat.name).includes(safeToLowerCase(selectedCategory)))

  return (
    <div className="py-16 bg-white">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Complete HR Functionality Implementation</h2>
          <p className="text-xl text-gray-600 mb-6">
            All {totalFunctions} HR functions implemented with full automation
          </p>

          <div className="flex justify-center items-center space-x-8 mb-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{implementedFunctions}</div>
              <div className="text-sm text-gray-600">Functions Implemented</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">100%</div>
              <div className="text-sm text-gray-600">Completion Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">12</div>
              <div className="text-sm text-gray-600">AI Agents Active</div>
            </div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
            <TabsList className="grid w-full grid-cols-4 lg:grid-cols-6">
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="talent">Talent</TabsTrigger>
              <TabsTrigger value="performance">Performance</TabsTrigger>
              <TabsTrigger value="payroll">Payroll</TabsTrigger>
              <TabsTrigger value="communication">Communication</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Functionality Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredCategories.map((category, index) => (
            <Card
              key={index}
              className={`border-2 border-${category.color}-200 bg-${category.color}-50 hover:shadow-lg transition-shadow`}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <category.icon className={`h-8 w-8 text-${category.color}-600`} />
                    <div>
                      <CardTitle className="text-lg">{category.name}</CardTitle>
                      <p className="text-sm text-gray-600">{category.count} Functions</p>
                    </div>
                  </div>
                  <Badge
                    variant={category.implemented ? "default" : "secondary"}
                    className={category.implemented ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}
                  >
                    {category.implemented ? "✓ Complete" : "Pending"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {category.functions.slice(0, 5).map((func, funcIndex) => (
                    <div key={funcIndex} className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span className="text-gray-700">{func}</span>
                    </div>
                  ))}
                  {category.functions.length > 5 && (
                    <div className="text-sm text-gray-500 font-medium">
                      +{category.functions.length - 5} more functions
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Implementation Status */}
        {/* Placeholder for Implementation Status section */}
      </div>
    </div>
  )
}
