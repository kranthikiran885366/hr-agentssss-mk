"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  TrendingUp,
  Calendar,
  Star,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Award,
  BookOpen,
  Users,
  ArrowRight,
  MapPin,
} from "lucide-react"

interface EmployeeJourney {
  employee_id: string
  tracked_at: string
  current_stage: string
  stage_history: StageHistory[]
  milestones: Milestone[]
  career_progression: CareerProgression
  performance_trends: PerformanceTrends
  engagement_metrics: EngagementMetrics
  risk_factors: RiskFactor[]
  recommendations: Recommendation[]
  predicted_outcomes: PredictedOutcomes
}

interface StageHistory {
  stage: string
  start_date: string
  end_date: string | null
  duration_days: number
  key_activities_completed: string[]
}

interface Milestone {
  type: string
  date: string
  description: string
}

interface CareerProgression {
  current_track: string
  current_level: string
  next_level: string
  progression_readiness: number
  time_in_current_level: number
  skills_for_next_level: string[]
  estimated_time_to_promotion: number
}

interface PerformanceTrends {
  overall_trend: string
  current_rating: number
  previous_rating: number
  improvement_areas: string[]
  strengths: string[]
}

interface EngagementMetrics {
  overall_score: number
  satisfaction_score: number
  commitment_score: number
  advocacy_score: number
  last_survey_date: string
}

interface RiskFactor {
  type: string
  severity: string
  description: string
  impact: string
}

interface Recommendation {
  type: string
  priority: string
  description: string
  actions: string[]
}

interface PredictedOutcomes {
  retention_probability: number
  promotion_probability: number
  performance_trajectory: string
  engagement_forecast: string
}

export function EmployeeJourneyTracker({ employeeId }: { employeeId: string }) {
  const [journeyData, setJourneyData] = useState<EmployeeJourney | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchJourneyData()
  }, [employeeId])

  const fetchJourneyData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/employee-lifecycle/journey/${employeeId}`)
      const data = await response.json()
      setJourneyData(data)
    } catch (error) {
      console.error("Failed to fetch journey data:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  if (!journeyData) {
    return <div className="text-center text-gray-500">No journey data available</div>
  }

  const getStageColor = (stage: string) => {
    const colors = {
      pre_hire: "bg-gray-500",
      onboarding: "bg-blue-500",
      probation: "bg-yellow-500",
      active_employment: "bg-green-500",
      career_transition: "bg-purple-500",
      pre_departure: "bg-orange-500",
      offboarding: "bg-red-500",
    }
    return colors[stage as keyof typeof colors] || "bg-gray-500"
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "text-red-600"
      case "medium":
        return "text-yellow-600"
      case "low":
        return "text-green-600"
      default:
        return "text-gray-600"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "destructive"
      case "medium":
        return "default"
      case "low":
        return "secondary"
      default:
        return "outline"
    }
  }

  return (
    <div className="space-y-6">
      {/* Journey Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Stage</p>
                <p className="text-lg font-bold capitalize">{journeyData.current_stage.replace("_", " ")}</p>
              </div>
              <MapPin className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Performance Rating</p>
                <p className="text-lg font-bold text-green-600">
                  {journeyData.performance_trends.current_rating.toFixed(1)}
                </p>
              </div>
              <Star className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Engagement Score</p>
                <p className="text-lg font-bold text-blue-600">{journeyData.engagement_metrics.overall_score}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Retention Risk</p>
                <p
                  className={`text-lg font-bold ${journeyData.predicted_outcomes.retention_probability > 80 ? "text-green-600" : "text-red-600"}`}
                >
                  {journeyData.predicted_outcomes.retention_probability}%
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Journey Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Employee Journey Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Stage Progress */}
            <div className="flex items-center justify-between overflow-x-auto pb-4">
              {journeyData.stage_history.map((stage, index) => (
                <div key={stage.stage} className="flex items-center">
                  <div className="flex flex-col items-center min-w-[120px]">
                    <div
                      className={`w-12 h-12 rounded-full ${getStageColor(stage.stage)} flex items-center justify-center text-white`}
                    >
                      {stage.end_date ? <CheckCircle className="h-6 w-6" /> : <Clock className="h-6 w-6" />}
                    </div>
                    <p className="text-sm font-medium mt-2 text-center capitalize">{stage.stage.replace("_", " ")}</p>
                    <p className="text-xs text-gray-500">{stage.duration_days} days</p>
                  </div>
                  {index < journeyData.stage_history.length - 1 && (
                    <ArrowRight className="h-6 w-6 text-gray-400 mx-4" />
                  )}
                </div>
              ))}
            </div>

            {/* Milestones */}
            <div>
              <h4 className="font-semibold mb-3">Key Milestones</h4>
              <div className="space-y-2">
                {journeyData.milestones.map((milestone, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <Award className="h-5 w-5 text-yellow-500" />
                    <div className="flex-1">
                      <p className="font-medium">{milestone.description}</p>
                      <p className="text-sm text-gray-600">{new Date(milestone.date).toLocaleDateString()}</p>
                    </div>
                    <Badge variant="outline" className="capitalize">
                      {milestone.type.replace("_", " ")}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analysis */}
      <Tabs defaultValue="progression" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="progression">Career</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="engagement">Engagement</TabsTrigger>
          <TabsTrigger value="risks">Risk Factors</TabsTrigger>
          <TabsTrigger value="recommendations">Actions</TabsTrigger>
        </TabsList>

        <TabsContent value="progression" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Career Progression
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Current Position</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Track:</span>
                      <Badge variant="outline" className="capitalize">
                        {journeyData.career_progression.current_track.replace("_", " ")}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Level:</span>
                      <Badge className="capitalize">{journeyData.career_progression.current_level}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Time in Level:</span>
                      <span>{journeyData.career_progression.time_in_current_level} days</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3">Next Level Progress</h4>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Readiness for {journeyData.career_progression.next_level}</span>
                        <span>{journeyData.career_progression.progression_readiness}%</span>
                      </div>
                      <Progress value={journeyData.career_progression.progression_readiness} className="h-2" />
                    </div>
                    <p className="text-sm text-gray-600">
                      Estimated time to promotion: {journeyData.career_progression.estimated_time_to_promotion} days
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-3">Skills for Next Level</h4>
                <div className="flex flex-wrap gap-2">
                  {journeyData.career_progression.skills_for_next_level.map((skill, index) => (
                    <Badge key={index} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Performance Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Performance Trend</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Current Rating:</span>
                      <span className="font-semibold text-green-600">
                        {journeyData.performance_trends.current_rating.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Previous Rating:</span>
                      <span className="font-semibold">{journeyData.performance_trends.previous_rating.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Trend:</span>
                      <Badge
                        variant={journeyData.performance_trends.overall_trend === "improving" ? "default" : "secondary"}
                      >
                        {journeyData.performance_trends.overall_trend}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3">Strengths</h4>
                  <div className="space-y-1">
                    {journeyData.performance_trends.strengths.map((strength, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-sm">{strength}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-3">Improvement Areas</h4>
                <div className="flex flex-wrap gap-2">
                  {journeyData.performance_trends.improvement_areas.map((area, index) => (
                    <Badge key={index} variant="outline">
                      {area}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="engagement" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Engagement Metrics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Overall Engagement</span>
                      <span>{journeyData.engagement_metrics.overall_score}%</span>
                    </div>
                    <Progress value={journeyData.engagement_metrics.overall_score} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Job Satisfaction</span>
                      <span>{journeyData.engagement_metrics.satisfaction_score}%</span>
                    </div>
                    <Progress value={journeyData.engagement_metrics.satisfaction_score} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Commitment</span>
                      <span>{journeyData.engagement_metrics.commitment_score}%</span>
                    </div>
                    <Progress value={journeyData.engagement_metrics.commitment_score} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Advocacy</span>
                      <span>{journeyData.engagement_metrics.advocacy_score}%</span>
                    </div>
                    <Progress value={journeyData.engagement_metrics.advocacy_score} className="h-2" />
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3">Survey Information</h4>
                  <p className="text-sm text-gray-600">
                    Last survey completed:{" "}
                    {new Date(journeyData.engagement_metrics.last_survey_date).toLocaleDateString()}
                  </p>
                  <Button size="sm" className="mt-3">
                    Schedule Follow-up Survey
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risks" className="space-y-4">
          <div className="space-y-4">
            {journeyData.risk_factors.map((risk, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className={`h-5 w-5 ${getSeverityColor(risk.severity)}`} />
                        <h4 className="font-semibold capitalize">{risk.type.replace("_", " ")}</h4>
                        <Badge
                          variant={
                            risk.severity === "high"
                              ? "destructive"
                              : risk.severity === "medium"
                                ? "default"
                                : "secondary"
                          }
                        >
                          {risk.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{risk.description}</p>
                      <p className="text-xs text-gray-500">Impact: {risk.impact.replace("_", " ")}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          <div className="space-y-4">
            {journeyData.recommendations.map((rec, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <BookOpen className="h-5 w-5 text-blue-500" />
                      <h4 className="font-semibold capitalize">{rec.type.replace("_", " ")}</h4>
                    </div>
                    <Badge variant={getPriorityColor(rec.priority)}>{rec.priority} priority</Badge>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">{rec.description}</p>

                  <div>
                    <h5 className="font-medium mb-2">Recommended Actions:</h5>
                    <ul className="space-y-1">
                      {rec.actions.map((action, actionIndex) => (
                        <li key={actionIndex} className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mt-3 flex gap-2">
                    <Button size="sm">Implement</Button>
                    <Button size="sm" variant="outline">
                      Schedule
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
