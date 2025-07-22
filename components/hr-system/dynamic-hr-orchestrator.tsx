
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import {
  Bot,
  Activity,
  Users,
  Calendar,
  DollarSign,
  TrendingUp,
  Shield,
  Brain,
  Zap,
  Globe,
  Award,
  Bell,
  Settings,
  AlertTriangle,
  CheckCircle,
  Clock,
  PlayCircle,
  PauseCircle,
  StopCircle
} from "lucide-react"

interface HRModule {
  id: string
  name: string
  category: string
  status: "active" | "processing" | "paused" | "error" | "completed"
  automation: number
  lastExecution: string
  nextExecution: string
  executionsToday: number
  successRate: number
  avgExecutionTime: string
  description: string
  dependencies: string[]
  dynamicFeatures: string[]
}

interface SystemMetrics {
  totalModules: number
  activeModules: number
  automationRate: number
  totalExecutions: number
  systemUptime: string
  aiConfidence: number
}

export function DynamicHROrchestrator() {
  const [modules, setModules] = useState<HRModule[]>([])
  const [metrics, setMetrics] = useState<SystemMetrics>({
    totalModules: 0,
    activeModules: 0,
    automationRate: 0,
    totalExecutions: 0,
    systemUptime: "99.8%",
    aiConfidence: 94.2
  })
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [isSystemRunning, setIsSystemRunning] = useState(true)

  useEffect(() => {
    initializeDynamicHRSystem()
    const interval = setInterval(updateSystemMetrics, 5000)
    return () => clearInterval(interval)
  }, [])

  const initializeDynamicHRSystem = () => {
    const hrModules: HRModule[] = [
      // Talent Acquisition Modules
      {
        id: "ta001",
        name: "AI Job Requisition Processor",
        category: "Talent Acquisition",
        status: "active",
        automation: 100,
        lastExecution: "2 min ago",
        nextExecution: "Continuous",
        executionsToday: 47,
        successRate: 98.5,
        avgExecutionTime: "1.2s",
        description: "Automatically processes job requisitions using NLP and creates optimized job descriptions",
        dependencies: [],
        dynamicFeatures: ["Auto JD Generation", "Multi-platform Posting", "Real-time Analytics"]
      },
      {
        id: "ta002",
        name: "Resume AI Analyzer",
        category: "Talent Acquisition",
        status: "processing",
        automation: 100,
        lastExecution: "Now",
        nextExecution: "Continuous",
        executionsToday: 234,
        successRate: 97.2,
        avgExecutionTime: "0.8s",
        description: "Real-time resume parsing with AI skill extraction and candidate ranking",
        dependencies: ["ta001"],
        dynamicFeatures: ["Deep Learning Parsing", "Bias-free Screening", "Cultural Fit Analysis"]
      },
      {
        id: "ta003",
        name: "AI Interview Conductor",
        category: "Talent Acquisition",
        status: "active",
        automation: 95,
        lastExecution: "5 min ago",
        nextExecution: "On Demand",
        executionsToday: 18,
        successRate: 94.7,
        avgExecutionTime: "23m",
        description: "Conducts full AI interviews with voice, video, and behavioral analysis",
        dependencies: ["ta002"],
        dynamicFeatures: ["Multi-modal Interview", "Emotion Detection", "Real-time Scoring"]
      },

      // Employee Lifecycle Modules
      {
        id: "el001",
        name: "Smart Onboarding Orchestrator",
        category: "Employee Lifecycle",
        status: "active",
        automation: 100,
        lastExecution: "1 hour ago",
        nextExecution: "On New Hire",
        executionsToday: 8,
        successRate: 100,
        avgExecutionTime: "2.1h",
        description: "End-to-end automated onboarding with document verification and system setup",
        dependencies: ["ta003"],
        dynamicFeatures: ["OCR Document Verification", "Auto Account Creation", "Virtual HR Buddy"]
      },
      {
        id: "el002",
        name: "Performance Intelligence Engine",
        category: "Employee Lifecycle",
        status: "active",
        automation: 92,
        lastExecution: "30 min ago",
        nextExecution: "Continuous",
        executionsToday: 156,
        successRate: 96.8,
        avgExecutionTime: "0.5s",
        description: "Real-time performance tracking with predictive analytics and automated feedback",
        dependencies: ["el001"],
        dynamicFeatures: ["360° AI Analysis", "Predictive Performance", "Auto Goal Setting"]
      },
      {
        id: "el003",
        name: "Learning Path Generator",
        category: "Employee Lifecycle",
        status: "active",
        automation: 88,
        lastExecution: "15 min ago",
        nextExecution: "Daily",
        executionsToday: 73,
        successRate: 93.4,
        avgExecutionTime: "3.2s",
        description: "Personalized learning paths with AI-curated content and progress tracking",
        dependencies: ["el002"],
        dynamicFeatures: ["Adaptive Learning", "Skill Gap Analysis", "Micro-learning Delivery"]
      },

      // Operational Excellence Modules
      {
        id: "oe001",
        name: "Smart Attendance System",
        category: "Operational Excellence",
        status: "active",
        automation: 100,
        lastExecution: "1 min ago",
        nextExecution: "Continuous",
        executionsToday: 1247,
        successRate: 99.7,
        avgExecutionTime: "0.1s",
        description: "Multi-modal attendance with face recognition, GPS, and behavioral patterns",
        dependencies: [],
        dynamicFeatures: ["Face Recognition", "Geo-fencing", "Pattern Analysis"]
      },
      {
        id: "oe002",
        name: "Payroll Intelligence Engine",
        category: "Operational Excellence",
        status: "active",
        automation: 100,
        lastExecution: "6 hours ago",
        nextExecution: "Monthly",
        executionsToday: 1,
        successRate: 100,
        avgExecutionTime: "12m",
        description: "Comprehensive payroll processing with statutory compliance and error detection",
        dependencies: ["oe001"],
        dynamicFeatures: ["Auto Compliance", "Error Detection", "Real-time Processing"]
      },
      {
        id: "oe003",
        name: "Employee Wellness Monitor",
        category: "Operational Excellence",
        status: "active",
        automation: 85,
        lastExecution: "10 min ago",
        nextExecution: "Continuous",
        executionsToday: 89,
        successRate: 91.2,
        avgExecutionTime: "2.1s",
        description: "Real-time wellness tracking with mood analysis and proactive interventions",
        dependencies: [],
        dynamicFeatures: ["Mood Analytics", "Stress Detection", "Wellness Recommendations"]
      },

      // Communication & Engagement Modules
      {
        id: "ce001",
        name: "AI Communication Hub",
        category: "Communication & Engagement",
        status: "active",
        automation: 95,
        lastExecution: "3 min ago",
        nextExecution: "Continuous",
        executionsToday: 456,
        successRate: 97.8,
        avgExecutionTime: "0.3s",
        description: "Multi-channel communication with personalized messaging and voice synthesis",
        dependencies: [],
        dynamicFeatures: ["Multi-channel Delivery", "Voice Synthesis", "Personalization AI"]
      },
      {
        id: "ce002",
        name: "Engagement Intelligence System",
        category: "Communication & Engagement",
        status: "active",
        automation: 90,
        lastExecution: "20 min ago",
        nextExecution: "Hourly",
        executionsToday: 24,
        successRate: 95.1,
        avgExecutionTime: "5.7s",
        description: "Predictive engagement analysis with automated pulse surveys and interventions",
        dependencies: ["ce001"],
        dynamicFeatures: ["Sentiment Analysis", "Predictive Engagement", "Auto Interventions"]
      },
      {
        id: "ce003",
        name: "Conflict Resolution AI",
        category: "Communication & Engagement",
        status: "active",
        automation: 78,
        lastExecution: "2 hours ago",
        nextExecution: "On Demand",
        executionsToday: 3,
        successRate: 89.3,
        avgExecutionTime: "45m",
        description: "AI-mediated conflict resolution with natural language processing and mediation",
        dependencies: ["ce002"],
        dynamicFeatures: ["NLP Mediation", "Emotion Recognition", "Resolution Tracking"]
      },

      // Compliance & Security Modules
      {
        id: "cs001",
        name: "Compliance Monitor",
        category: "Compliance & Security",
        status: "active",
        automation: 100,
        lastExecution: "5 min ago",
        nextExecution: "Continuous",
        executionsToday: 287,
        successRate: 99.2,
        avgExecutionTime: "0.4s",
        description: "Real-time compliance monitoring with automated reporting and risk assessment",
        dependencies: [],
        dynamicFeatures: ["Real-time Monitoring", "Risk Assessment", "Auto Reporting"]
      },
      {
        id: "cs002",
        name: "Security Intelligence Engine",
        category: "Compliance & Security",
        status: "active",
        automation: 95,
        lastExecution: "1 min ago",
        nextExecution: "Continuous",
        executionsToday: 1456,
        successRate: 98.9,
        avgExecutionTime: "0.2s",
        description: "Advanced security monitoring with threat detection and access management",
        dependencies: ["cs001"],
        dynamicFeatures: ["Threat Detection", "Behavioral Analysis", "Auto Response"]
      },

      // Analytics & Intelligence Modules
      {
        id: "ai001",
        name: "HR Analytics Engine",
        category: "Analytics & Intelligence",
        status: "active",
        automation: 100,
        lastExecution: "1 min ago",
        nextExecution: "Continuous",
        executionsToday: 2847,
        successRate: 99.8,
        avgExecutionTime: "0.1s",
        description: "Real-time analytics with predictive insights and automated reporting",
        dependencies: [],
        dynamicFeatures: ["Predictive Analytics", "Real-time Dashboards", "Auto Insights"]
      },
      {
        id: "ai002",
        name: "Decision Intelligence System",
        category: "Analytics & Intelligence",
        status: "active",
        automation: 87,
        lastExecution: "10 min ago",
        nextExecution: "Hourly",
        executionsToday: 24,
        successRate: 94.6,
        avgExecutionTime: "12.3s",
        description: "AI-powered decision support with scenario analysis and recommendation engine",
        dependencies: ["ai001"],
        dynamicFeatures: ["Scenario Modeling", "Decision Trees", "Risk Analysis"]
      }
    ]

    setModules(hrModules)
    
    // Calculate metrics
    setMetrics({
      totalModules: hrModules.length,
      activeModules: hrModules.filter(m => m.status === "active").length,
      automationRate: hrModules.reduce((sum, m) => sum + m.automation, 0) / hrModules.length,
      totalExecutions: hrModules.reduce((sum, m) => sum + m.executionsToday, 0),
      systemUptime: "99.8%",
      aiConfidence: 94.2
    })
  }

  const updateSystemMetrics = () => {
    setModules(prev => prev.map(module => ({
      ...module,
      executionsToday: module.executionsToday + Math.floor(Math.random() * 2),
      successRate: Math.min(100, module.successRate + (Math.random() - 0.5) * 0.1)
    })))
  }

  const toggleModuleStatus = (moduleId: string) => {
    setModules(prev => prev.map(module => 
      module.id === moduleId 
        ? { 
            ...module, 
            status: module.status === "active" ? "paused" : "active" as any
          }
        : module
    ))
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return <CheckCircle className="h-4 w-4 text-green-600" />
      case "processing": return <Activity className="h-4 w-4 text-blue-600 animate-pulse" />
      case "paused": return <PauseCircle className="h-4 w-4 text-yellow-600" />
      case "error": return <AlertTriangle className="h-4 w-4 text-red-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-800"
      case "processing": return "bg-blue-100 text-blue-800"
      case "paused": return "bg-yellow-100 text-yellow-800"
      case "error": return "bg-red-100 text-red-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  const categories = ["all", "Talent Acquisition", "Employee Lifecycle", "Operational Excellence", "Communication & Engagement", "Compliance & Security", "Analytics & Intelligence"]

  const filteredModules = selectedCategory === "all" 
    ? modules 
    : modules.filter(m => m.category === selectedCategory)

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 min-h-screen">
      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Modules</p>
                <p className="text-2xl font-bold">{metrics.totalModules}</p>
              </div>
              <Bot className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Modules</p>
                <p className="text-2xl font-bold text-green-600">{metrics.activeModules}</p>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Automation Rate</p>
                <p className="text-2xl font-bold">{metrics.automationRate.toFixed(1)}%</p>
              </div>
              <Zap className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Executions Today</p>
                <p className="text-2xl font-bold">{metrics.totalExecutions.toLocaleString()}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Dynamic HR System Control Center</span>
            <div className="flex items-center space-x-4">
              <Badge variant={isSystemRunning ? "default" : "secondary"}>
                {isSystemRunning ? "System Active" : "System Paused"}
              </Badge>
              <Button
                variant={isSystemRunning ? "destructive" : "default"}
                onClick={() => setIsSystemRunning(!isSystemRunning)}
                className="flex items-center space-x-2"
              >
                {isSystemRunning ? <PauseCircle className="h-4 w-4" /> : <PlayCircle className="h-4 w-4" />}
                <span>{isSystemRunning ? "Pause System" : "Start System"}</span>
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <Brain className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <p className="text-sm font-medium">AI Confidence</p>
              <p className="text-lg font-bold">{metrics.aiConfidence}%</p>
            </div>
            <div className="text-center">
              <Shield className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <p className="text-sm font-medium">System Uptime</p>
              <p className="text-lg font-bold">{metrics.systemUptime}</p>
            </div>
            <div className="text-center">
              <Globe className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Global Reach</p>
              <p className="text-lg font-bold">24/7</p>
            </div>
            <div className="text-center">
              <Award className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Success Rate</p>
              <p className="text-lg font-bold">96.8%</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map(category => (
          <Button
            key={category}
            variant={selectedCategory === category ? "default" : "outline"}
            onClick={() => setSelectedCategory(category)}
            className="capitalize"
          >
            {category}
          </Button>
        ))}
      </div>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredModules.map(module => (
          <Card key={module.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-lg">
                <span>{module.name}</span>
                {getStatusIcon(module.status)}
              </CardTitle>
              <div className="flex items-center justify-between">
                <Badge className={getStatusColor(module.status)}>
                  {module.status}
                </Badge>
                <Badge variant="outline">{module.category}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">{module.description}</p>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Automation Level</span>
                  <span className="font-medium">{module.automation}%</span>
                </div>
                <Progress value={module.automation} className="h-2" />
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Executions Today</p>
                  <p className="font-medium">{module.executionsToday}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Success Rate</p>
                  <p className="font-medium">{module.successRate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Last Run</p>
                  <p className="font-medium">{module.lastExecution}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Avg Time</p>
                  <p className="font-medium">{module.avgExecutionTime}</p>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Dynamic Features:</p>
                <div className="flex flex-wrap gap-1">
                  {module.dynamicFeatures.map(feature => (
                    <Badge key={feature} variant="secondary" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant={module.status === "active" ? "destructive" : "default"}
                  onClick={() => toggleModuleStatus(module.id)}
                  className="flex-1"
                >
                  {module.status === "active" ? "Pause" : "Activate"}
                </Button>
                <Button size="sm" variant="outline" className="flex-1">
                  <Settings className="h-4 w-4 mr-1" />
                  Configure
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Real-time Activity Feed */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bell className="h-5 w-5 mr-2" />
            Real-time Activity Feed
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {modules.slice(0, 10).map(module => (
              <div key={module.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(module.status)}
                  <span className="text-sm">{module.name}</span>
                </div>
                <span className="text-xs text-muted-foreground">{module.lastExecution}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
