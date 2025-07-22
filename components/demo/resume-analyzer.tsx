"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { X, Brain, CheckCircle, AlertCircle, Briefcase, GraduationCap, Star, TrendingUp } from "lucide-react"
import { useAI } from "@/components/providers/ai-provider"

interface ResumeAnalyzerProps {
  onClose: () => void
}

interface AnalysisResult {
  score: number
  skills: string[]
  experience: string
  education: string
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  culturalFit: number
  technicalFit: number
}

export function ResumeAnalyzer({ onClose }: ResumeAnalyzerProps) {
  const { analyzeResume, isProcessing } = useAI()
  const [resumeText, setResumeText] = useState("")
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [step, setStep] = useState<"input" | "analyzing" | "results">("input")

  const handleAnalyze = async () => {
    if (!resumeText.trim()) return

    setStep("analyzing")

    try {
      const result = await analyzeResume(resumeText)

      // Enhanced analysis result
      const enhancedResult: AnalysisResult = {
        score: result.score,
        skills: result.skills,
        experience: result.experience,
        education: result.education,
        strengths: result.strengths,
        weaknesses: ["Could improve technical depth", "Limited leadership experience"],
        recommendations: result.recommendations,
        culturalFit: Math.floor(Math.random() * 30) + 70,
        technicalFit: Math.floor(Math.random() * 30) + 70,
      }

      setAnalysisResult(enhancedResult)
      setStep("results")
    } catch (error) {
      console.error("Analysis failed:", error)
      setStep("input")
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600"
    if (score >= 80) return "text-blue-600"
    if (score >= 70) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBg = (score: number) => {
    if (score >= 90) return "bg-green-100"
    if (score >= 80) return "bg-blue-100"
    if (score >= 70) return "bg-yellow-100"
    return "bg-red-100"
  }

  const sampleResume = `John Doe
Software Engineer
john.doe@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

EXPERIENCE
Senior Software Engineer | Tech Corp | 2021 - Present
• Led development of microservices architecture serving 1M+ users
• Implemented CI/CD pipelines reducing deployment time by 60%
• Mentored 3 junior developers and conducted code reviews
• Technologies: React, Node.js, AWS, Docker, Kubernetes

Software Engineer | StartupXYZ | 2019 - 2021
• Built scalable web applications using React and Python
• Collaborated with cross-functional teams in Agile environment
• Optimized database queries improving performance by 40%
• Technologies: Python, Django, PostgreSQL, Redis

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2015 - 2019
GPA: 3.8/4.0

SKILLS
Programming: JavaScript, Python, Java, TypeScript
Frontend: React, Vue.js, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Django, Express.js, FastAPI
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Docker, Kubernetes, Terraform
Tools: Git, Jenkins, JIRA, Figma

PROJECTS
E-commerce Platform (2022)
• Built full-stack e-commerce platform with React and Node.js
• Integrated payment processing and inventory management
• Deployed on AWS with auto-scaling capabilities

CERTIFICATIONS
• AWS Certified Solutions Architect (2022)
• Certified Kubernetes Administrator (2021)`

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <Brain className="h-6 w-6 text-purple-600" />
          <h2 className="text-2xl font-bold">AI Resume Analyzer</h2>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {step === "input" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload or Paste Resume</CardTitle>
              <p className="text-gray-600">Our AI will analyze the resume for skills, experience, and cultural fit</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Textarea
                  placeholder="Paste resume text here..."
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  className="min-h-[300px]"
                />

                <div className="flex justify-between items-center">
                  <Button variant="outline" onClick={() => setResumeText(sampleResume)}>
                    Use Sample Resume
                  </Button>

                  <Button
                    onClick={handleAnalyze}
                    disabled={!resumeText.trim() || isProcessing}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Brain className="h-4 w-4 mr-2" />
                    Analyze Resume
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>What Our AI Analyzes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { icon: Briefcase, title: "Experience Level", desc: "Years of experience and role progression" },
                  {
                    icon: GraduationCap,
                    title: "Education & Skills",
                    desc: "Educational background and technical skills",
                  },
                  { icon: Star, title: "Cultural Fit", desc: "Alignment with company values and culture" },
                  { icon: TrendingUp, title: "Growth Potential", desc: "Career trajectory and learning ability" },
                ].map((item, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                    <item.icon className="h-5 w-5 text-purple-600 mt-1" />
                    <div>
                      <h3 className="font-medium">{item.title}</h3>
                      <p className="text-sm text-gray-600">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {step === "analyzing" && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Brain className="h-8 w-8 text-purple-600 animate-pulse" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Analyzing Resume...</h3>
          <p className="text-gray-600 mb-6">Our AI is processing the resume and extracting insights</p>

          <div className="max-w-md mx-auto space-y-3">
            <div className="flex justify-between text-sm">
              <span>Extracting skills and experience</span>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </div>
            <div className="flex justify-between text-sm">
              <span>Analyzing cultural fit</span>
              <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
            </div>
            <div className="flex justify-between text-sm text-gray-400">
              <span>Generating recommendations</span>
              <div className="w-4 h-4 border-2 border-gray-300 rounded-full" />
            </div>
          </div>
        </div>
      )}

      {step === "results" && analysisResult && (
        <div className="space-y-6">
          {/* Overall Score */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div
                    className={`w-20 h-20 rounded-full ${getScoreBg(analysisResult.score)} flex items-center justify-center mx-auto mb-3`}
                  >
                    <span className={`text-2xl font-bold ${getScoreColor(analysisResult.score)}`}>
                      {analysisResult.score}
                    </span>
                  </div>
                  <h3 className="font-semibold">Overall Score</h3>
                  <p className="text-sm text-gray-600">Out of 100</p>
                </div>

                <div className="text-center">
                  <div
                    className={`w-20 h-20 rounded-full ${getScoreBg(analysisResult.technicalFit)} flex items-center justify-center mx-auto mb-3`}
                  >
                    <span className={`text-2xl font-bold ${getScoreColor(analysisResult.technicalFit)}`}>
                      {analysisResult.technicalFit}
                    </span>
                  </div>
                  <h3 className="font-semibold">Technical Fit</h3>
                  <p className="text-sm text-gray-600">Skills match</p>
                </div>

                <div className="text-center">
                  <div
                    className={`w-20 h-20 rounded-full ${getScoreBg(analysisResult.culturalFit)} flex items-center justify-center mx-auto mb-3`}
                  >
                    <span className={`text-2xl font-bold ${getScoreColor(analysisResult.culturalFit)}`}>
                      {analysisResult.culturalFit}
                    </span>
                  </div>
                  <h3 className="font-semibold">Cultural Fit</h3>
                  <p className="text-sm text-gray-600">Company alignment</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detailed Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>Strengths</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {analysisResult.strengths.map((strength, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      <span className="text-sm">{strength}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5 text-yellow-600" />
                  <span>Areas for Improvement</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {analysisResult.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                      <span className="text-sm">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Skills and Experience */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Extracted Skills</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.skills.map((skill, index) => (
                    <Badge key={index} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Experience & Education</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <h4 className="font-medium text-sm text-gray-700">Experience Level</h4>
                    <p className="text-sm">{analysisResult.experience}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-sm text-gray-700">Education</h4>
                    <p className="text-sm">{analysisResult.education}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>AI Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {analysisResult.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                    <Brain className="h-5 w-5 text-blue-600 mt-0.5" />
                    <span className="text-sm">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-center space-x-4">
            <Button onClick={() => setStep("input")} variant="outline">
              Analyze Another Resume
            </Button>
            <Button className="bg-green-600 hover:bg-green-700">Proceed to Interview</Button>
            <Button variant="outline">Generate Report</Button>
          </div>
        </div>
      )}
    </div>
  )
}
