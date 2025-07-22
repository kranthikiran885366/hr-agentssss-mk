"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { CheckCircle, Clock, User, Star, MapPin, Calendar } from "lucide-react"

interface MentorAssignmentStepProps {
  onNext: () => void
  onPrevious: () => void
}

interface Mentor {
  id: string
  name: string
  role: string
  department: string
  experience: number
  location: string
  avatar?: string
  skills: string[]
  rating: number
  availability: string
}

export function MentorAssignmentStep({ onNext, onPrevious }: MentorAssignmentStepProps) {
  const [assignmentStatus, setAssignmentStatus] = useState<"analyzing" | "matching" | "assigned">("analyzing")
  const [assignedMentor, setAssignedMentor] = useState<Mentor | null>(null)

  const potentialMentors: Mentor[] = [
    {
      id: "1",
      name: "Sarah Johnson",
      role: "Senior Software Engineer",
      department: "Engineering",
      experience: 8,
      location: "San Francisco, CA",
      skills: ["React", "Node.js", "Python", "Team Leadership"],
      rating: 4.9,
      availability: "Available",
    },
    {
      id: "2",
      name: "Michael Chen",
      role: "Product Manager",
      department: "Product",
      experience: 6,
      location: "New York, NY",
      skills: ["Product Strategy", "Agile", "Data Analysis", "Mentoring"],
      rating: 4.8,
      availability: "Available",
    },
    {
      id: "3",
      name: "Emily Rodriguez",
      role: "UX Design Lead",
      department: "Design",
      experience: 7,
      location: "Austin, TX",
      skills: ["UI/UX Design", "Figma", "User Research", "Design Systems"],
      rating: 4.9,
      availability: "Available",
    },
  ]

  useEffect(() => {
    const assignMentor = async () => {
      // Simulate analysis phase
      await new Promise((resolve) => setTimeout(resolve, 2000))
      setAssignmentStatus("matching")

      // Simulate matching phase
      await new Promise((resolve) => setTimeout(resolve, 3000))

      // Assign a mentor (simulate ML matching)
      const selectedMentor = potentialMentors[Math.floor(Math.random() * potentialMentors.length)]
      setAssignedMentor(selectedMentor)
      setAssignmentStatus("assigned")
    }

    assignMentor()
  }, [])

  const getStatusMessage = () => {
    switch (assignmentStatus) {
      case "analyzing":
        return "Analyzing your profile and preferences..."
      case "matching":
        return "Finding the perfect mentor match..."
      case "assigned":
        return "Mentor successfully assigned!"
      default:
        return "Processing..."
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="h-6 w-6 text-blue-600" />
            <span>Mentor Assignment</span>
          </CardTitle>
          <p className="text-gray-600">
            Our AI system is finding the perfect mentor based on your background and career goals.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 mb-4">
                {assignmentStatus !== "assigned" ? (
                  <Clock className="h-6 w-6 text-blue-600 animate-spin" />
                ) : (
                  <CheckCircle className="h-6 w-6 text-green-600" />
                )}
                <span className="text-lg font-medium">{getStatusMessage()}</span>
              </div>

              {assignmentStatus !== "assigned" && (
                <div className="max-w-md mx-auto">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-medium text-blue-900 mb-2">Matching Criteria</h3>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Skills and expertise alignment</li>
                      <li>• Department and role compatibility</li>
                      <li>• Availability and workload</li>
                      <li>• Mentoring experience and ratings</li>
                      <li>• Geographic proximity</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

            {assignmentStatus === "assigned" && assignedMentor && (
              <div className="max-w-2xl mx-auto">
                <div className="border rounded-lg p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
                  <div className="flex items-start space-x-4">
                    <Avatar className="h-16 w-16">
                      <AvatarImage src={assignedMentor.avatar || "/placeholder.svg"} />
                      <AvatarFallback className="bg-blue-600 text-white text-lg">
                        {assignedMentor.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>

                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900">{assignedMentor.name}</h3>
                        <Badge className="bg-green-100 text-green-800">Your Mentor</Badge>
                      </div>

                      <p className="text-gray-600 mb-2">{assignedMentor.role}</p>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <MapPin className="h-4 w-4" />
                          <span>{assignedMentor.location}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Calendar className="h-4 w-4" />
                          <span>{assignedMentor.experience} years experience</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Star className="h-4 w-4 text-yellow-500" />
                          <span>{assignedMentor.rating}/5.0 rating</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span>{assignedMentor.availability}</span>
                        </div>
                      </div>

                      <div className="mb-4">
                        <h4 className="font-medium text-gray-900 mb-2">Expertise Areas</h4>
                        <div className="flex flex-wrap gap-2">
                          {assignedMentor.skills.map((skill, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">Next Steps</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span>Introduction email sent to both parties</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span>Calendar invite for first meeting scheduled</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-blue-600" />
                        <span>Mentorship guidelines shared</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">Contact Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <p>
                        <strong>Email:</strong> {assignedMentor.name.toLowerCase().replace(" ", ".")}@company.com
                      </p>
                      <p>
                        <strong>Slack:</strong> @{assignedMentor.name.toLowerCase().replace(" ", "")}
                      </p>
                      <p>
                        <strong>Department:</strong> {assignedMentor.department}
                      </p>
                      <p className="text-gray-600 text-xs mt-2">
                        Your mentor will reach out within 24 hours to schedule your first meeting.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={onNext} disabled={assignmentStatus !== "assigned"}>
          {assignmentStatus === "assigned" ? "Complete Onboarding" : "Assigning Mentor..."}
        </Button>
      </div>
    </div>
  )
}
