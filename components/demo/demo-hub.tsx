"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Bot, Mic, MessageSquare, FileText, Phone, Users, Brain, Zap, Play, ArrowRight } from "lucide-react"
import { VoiceDemo } from "@/components/voice/voice-demo"
import { ChatDemo } from "@/components/chat/chat-demo"
import { ResumeAnalyzer } from "@/components/demo/resume-analyzer"
import { CallSimulator } from "@/components/demo/call-simulator"
import { OnboardingDemo } from "@/components/demo/onboarding-demo"

export function DemoHub() {
  const [activeDemo, setActiveDemo] = useState<string | null>(null)

  const demos = [
    {
      id: "voice-interview",
      title: "Voice Interview Agent",
      description: "Experience AI-powered voice interviews with real-time speech recognition and natural conversation",
      icon: Mic,
      color: "bg-blue-500",
      features: ["Real-time speech recognition", "Natural conversation flow", "Emotion detection", "Instant scoring"],
      component: VoiceDemo,
    },
    {
      id: "chat-interview",
      title: "Chat Interview Bot",
      description: "Interactive chat-based interviews with dynamic question generation and real-time analysis",
      icon: MessageSquare,
      color: "bg-green-500",
      features: ["Dynamic questioning", "Real-time scoring", "Behavioral analysis", "Instant feedback"],
      component: ChatDemo,
    },
    {
      id: "resume-analyzer",
      title: "AI Resume Analyzer",
      description: "Advanced NLP-powered resume screening with skill extraction and candidate matching",
      icon: FileText,
      color: "bg-purple-500",
      features: ["Skill extraction", "Experience analysis", "Cultural fit scoring", "Automated ranking"],
      component: ResumeAnalyzer,
    },
    {
      id: "call-simulator",
      title: "Automated Calling",
      description: "AI agent that makes outbound calls to candidates, managers, and references",
      icon: Phone,
      color: "bg-orange-500",
      features: ["Natural conversation", "Call recording", "Summary generation", "Follow-up scheduling"],
      component: CallSimulator,
    },
    {
      id: "onboarding-demo",
      title: "Smart Onboarding",
      description: "Complete onboarding automation with document verification and account setup",
      icon: Users,
      color: "bg-indigo-500",
      features: ["Document verification", "Account creation", "Mentor assignment", "Progress tracking"],
      component: OnboardingDemo,
    },
  ]

  const ActiveComponent = demos.find((demo) => demo.id === activeDemo)?.component

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Bot className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">HR Agent AI - Demo Hub</span>
            </div>
            <Button variant="outline" onClick={() => setActiveDemo(null)}>
              Back to Demos
            </Button>
          </div>
        </div>
      </header>

      {activeDemo && ActiveComponent ? (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 pt-20">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
            <ActiveComponent onClose={() => setActiveDemo(null)} />
          </div>
        </div>
      ) : (
        <div className="py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* Hero Section */}
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Experience the Future of HR Automation</h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Try our AI-powered HR tools that work like real humans. Each demo showcases different aspects of our
                comprehensive HR automation platform.
              </p>
            </div>

            {/* Demo Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {demos.map((demo) => (
                <Card
                  key={demo.id}
                  className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                >
                  <CardHeader>
                    <div className={`w-12 h-12 ${demo.color} rounded-lg flex items-center justify-center mb-4`}>
                      <demo.icon className="h-6 w-6 text-white" />
                    </div>
                    <CardTitle className="text-xl">{demo.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-4">{demo.description}</p>

                    <div className="space-y-2 mb-6">
                      {demo.features.map((feature, index) => (
                        <div key={index} className="flex items-center text-sm text-gray-700">
                          <Zap className="h-3 w-3 text-blue-500 mr-2" />
                          {feature}
                        </div>
                      ))}
                    </div>

                    <Button
                      onClick={() => setActiveDemo(demo.id)}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Try Demo
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Features Overview */}
            <div className="mt-16">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Complete HR Automation Pipeline</h2>
                <p className="text-lg text-gray-600">
                  See how our AI agents handle the entire hiring process from start to finish
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-8">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  {[
                    { step: 1, title: "Resume Screening", desc: "AI analyzes and scores resumes", icon: FileText },
                    { step: 2, title: "Interview", desc: "Voice/chat AI interviews", icon: Mic },
                    { step: 3, title: "Communication", desc: "Automated calling & messaging", icon: Phone },
                    { step: 4, title: "Offer Process", desc: "Letter generation & negotiation", icon: Brain },
                    { step: 5, title: "Onboarding", desc: "Complete automation", icon: Users },
                  ].map((item, index) => (
                    <div key={index} className="text-center">
                      <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full flex items-center justify-center mx-auto mb-4">
                        <item.icon className="h-6 w-6" />
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                      <p className="text-sm text-gray-600">{item.desc}</p>
                      {index < 4 && <ArrowRight className="h-5 w-5 text-gray-400 mx-auto mt-4 hidden md:block" />}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Call to Action */}
            <div className="mt-16 text-center">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
                <h2 className="text-2xl font-bold mb-4">Ready to Transform Your HR Operations?</h2>
                <p className="text-lg mb-6 opacity-90">
                  Experience the power of AI-driven HR automation that works 24/7
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
                    Schedule Live Demo
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-white text-white hover:bg-white hover:text-blue-600"
                  >
                    Contact Sales
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
