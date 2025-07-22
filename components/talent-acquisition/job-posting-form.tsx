"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Checkbox } from "@/components/ui/checkbox"
import { MapPin, DollarSign, Target, Sparkles, Send, Save, Eye } from "lucide-react"

interface JobPostingFormProps {
  onSubmit?: (jobData: any) => void
  initialData?: any
}

interface FormDataType {
  [key: string]: any;
}

export function JobPostingForm({ onSubmit, initialData }: JobPostingFormProps) {
  const [formData, setFormData] = useState<FormDataType>({
    title: initialData?.title || "",
    department: initialData?.department || "",
    location: initialData?.location || "",
    employment_type: initialData?.employment_type || "full_time",
    experience_level: initialData?.experience_level || "mid",
    description: initialData?.description || "",
    requirements: initialData?.requirements || [],
    responsibilities: initialData?.responsibilities || [],
    benefits: initialData?.benefits || [],
    salary_min: initialData?.salary_range?.min || 60000,
    salary_max: initialData?.salary_range?.max || 100000,
    skills_required: initialData?.skills_required || [],
    posting_channels: initialData?.posting_channels || [],
    approvers: initialData?.approvers || [],
    approval_status: initialData?.approval_status || "pending_approval",
    approval_history: initialData?.approval_history || [],
    ...initialData,
  })

  const [newRequirement, setNewRequirement] = useState("")
  const [newResponsibility, setNewResponsibility] = useState("")
  const [newBenefit, setNewBenefit] = useState("")
  const [newSkill, setNewSkill] = useState("")
  const [aiOptimizing, setAiOptimizing] = useState(false)
  const [submitResult, setSubmitResult] = useState<any>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev: FormDataType) => ({ ...prev, [field]: value }))
  }

  const addListItem = (field: string, value: string, setter: (value: string) => void) => {
    if (value.trim()) {
      setFormData((prev: FormDataType) => ({
        ...prev,
        [field]: [...prev[field], value.trim()],
      }))
      setter("")
    }
  }

  const removeListItem = (field: string, index: number) => {
    setFormData((prev: FormDataType) => ({
      ...prev,
      [field]: prev[field].filter((_: any, i: number) => i !== index),
    }))
  }

  const handleAIOptimization = async () => {
    setAiOptimizing(true)
    // Simulate AI optimization
    setTimeout(() => {
      setFormData((prev) => ({
        ...prev,
        description:
          prev.description +
          "\n\nAI-Enhanced: This role offers excellent growth opportunities in a collaborative environment with cutting-edge technology and inclusive culture.",
      }))
      setAiOptimizing(false)
    }, 2000)
  }

  const handleSubmit = async (action: "save" | "publish") => {
    const jobData = {
      ...formData,
      salary_range: {
        min: formData.salary_min,
        max: formData.salary_max,
      },
      status: action === "publish" ? "draft" : "draft", // Always draft until approved
      approval_status: "pending_approval",
    }
    setSubmitting(true)
    try {
      const res = await fetch("/api/talent-acquisition/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jobData),
      })
      const data = await res.json()
      setSubmitResult(data)
      if (onSubmit) onSubmit(data)
    } catch (err) {
      setSubmitResult({ error: "Failed to submit job posting" })
    } finally {
      setSubmitting(false)
    }
  }

  const availableChannels = [
    { id: "company_website", name: "Company Website", cost: 0 },
    { id: "linkedin", name: "LinkedIn", cost: 299 },
    { id: "indeed", name: "Indeed", cost: 199 },
    { id: "glassdoor", name: "Glassdoor", cost: 249 },
    { id: "stackoverflow", name: "Stack Overflow", cost: 199 },
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Create Job Posting
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Approval Status UI */}
          {formData.approval_status && (
            <div className="mb-4">
              <span className="font-semibold">Approval Status:</span> {formData.approval_status.replace("_", " ")}
              {Array.isArray(formData.approval_history) && formData.approval_history.length > 0 && (
                <div className="mt-2">
                  <span className="font-semibold">Approval History:</span>
                  <ul className="list-disc ml-6">
                    {formData.approval_history.map((entry: any, idx: number) => (
                      <li key={idx}>
                        {entry.action} by {entry.approver_id} at {entry.timestamp}
                        {entry.comment && `: ${entry.comment}`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          <Tabs defaultValue="basic" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="basic">Basic Info</TabsTrigger>
              <TabsTrigger value="details">Job Details</TabsTrigger>
              <TabsTrigger value="compensation">Compensation</TabsTrigger>
              <TabsTrigger value="posting">Posting</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Job Title</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => handleInputChange("title", e.target.value)}
                    placeholder="e.g. Senior Software Engineer"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Select value={formData.department} onValueChange={(value) => handleInputChange("department", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="engineering">Engineering</SelectItem>
                      <SelectItem value="product">Product</SelectItem>
                      <SelectItem value="design">Design</SelectItem>
                      <SelectItem value="marketing">Marketing</SelectItem>
                      <SelectItem value="sales">Sales</SelectItem>
                      <SelectItem value="hr">Human Resources</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4 text-gray-500" />
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) => handleInputChange("location", e.target.value)}
                      placeholder="e.g. San Francisco, CA or Remote"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="employment_type">Employment Type</Label>
                  <Select
                    value={formData.employment_type}
                    onValueChange={(value) => handleInputChange("employment_type", value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full_time">Full Time</SelectItem>
                      <SelectItem value="part_time">Part Time</SelectItem>
                      <SelectItem value="contract">Contract</SelectItem>
                      <SelectItem value="internship">Internship</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="experience_level">Experience Level</Label>
                  <Select
                    value={formData.experience_level}
                    onValueChange={(value) => handleInputChange("experience_level", value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="entry">Entry Level</SelectItem>
                      <SelectItem value="mid">Mid Level</SelectItem>
                      <SelectItem value="senior">Senior Level</SelectItem>
                      <SelectItem value="lead">Lead/Principal</SelectItem>
                      <SelectItem value="executive">Executive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="description">Job Description</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleAIOptimization}
                    disabled={aiOptimizing}
                    className="flex items-center gap-2 bg-transparent"
                  >
                    <Sparkles className="h-4 w-4" />
                    {aiOptimizing ? "Optimizing..." : "AI Optimize"}
                  </Button>
                </div>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange("description", e.target.value)}
                  placeholder="Describe the role, company culture, and what makes this opportunity exciting..."
                  rows={6}
                />
              </div>
            </TabsContent>

            <TabsContent value="details" className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label>Requirements</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      value={newRequirement}
                      onChange={(e) => setNewRequirement(e.target.value)}
                      placeholder="Add a requirement..."
                      onKeyPress={(e) =>
                        e.key === "Enter" && addListItem("requirements", newRequirement, setNewRequirement)
                      }
                    />
                    <Button onClick={() => addListItem("requirements", newRequirement, setNewRequirement)}>Add</Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.requirements.map((req: string, index: number) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="cursor-pointer"
                        onClick={() => removeListItem("requirements", index)}
                      >
                        {req} ×
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label>Responsibilities</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      value={newResponsibility}
                      onChange={(e) => setNewResponsibility(e.target.value)}
                      placeholder="Add a responsibility..."
                      onKeyPress={(e) =>
                        e.key === "Enter" && addListItem("responsibilities", newResponsibility, setNewResponsibility)
                      }
                    />
                    <Button onClick={() => addListItem("responsibilities", newResponsibility, setNewResponsibility)}>
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.responsibilities.map((resp: string, index: number) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="cursor-pointer"
                        onClick={() => removeListItem("responsibilities", index)}
                      >
                        {resp} ×
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label>Required Skills</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      placeholder="Add a skill..."
                      onKeyPress={(e) => e.key === "Enter" && addListItem("skills_required", newSkill, setNewSkill)}
                    />
                    <Button onClick={() => addListItem("skills_required", newSkill, setNewSkill)}>Add</Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.skills_required.map((skill: string, index: number) => (
                      <Badge
                        key={index}
                        variant="outline"
                        className="cursor-pointer"
                        onClick={() => removeListItem("skills_required", index)}
                      >
                        {skill} ×
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label>Benefits</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      value={newBenefit}
                      onChange={(e) => setNewBenefit(e.target.value)}
                      placeholder="Add a benefit..."
                      onKeyPress={(e) => e.key === "Enter" && addListItem("benefits", newBenefit, setNewBenefit)}
                    />
                    <Button onClick={() => addListItem("benefits", newBenefit, setNewBenefit)}>Add</Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.benefits.map((benefit: string, index: number) => (
                      <Badge
                        key={index}
                        variant="default"
                        className="cursor-pointer"
                        onClick={() => removeListItem("benefits", index)}
                      >
                        {benefit} ×
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="compensation" className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  <DollarSign className="h-5 w-5" />
                  <h3 className="text-lg font-semibold">Salary Range</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="salary_min">Minimum Salary</Label>
                    <Input
                      id="salary_min"
                      type="number"
                      value={formData.salary_min}
                      onChange={(e) => handleInputChange("salary_min", Number.parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="salary_max">Maximum Salary</Label>
                    <Input
                      id="salary_max"
                      type="number"
                      value={formData.salary_max}
                      onChange={(e) => handleInputChange("salary_max", Number.parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium mb-2">Market Analysis</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Market Median:</span>
                      <div className="font-semibold">
                        ${((formData.salary_min + formData.salary_max) / 2).toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Competitiveness:</span>
                      <div className="font-semibold text-green-600">Above Market</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Est. Applications:</span>
                      <div className="font-semibold">45-60</div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="posting" className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  <Send className="h-5 w-5" />
                  <h3 className="text-lg font-semibold">Posting Channels</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {availableChannels.map((channel) => (
                    <div key={channel.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                      <Checkbox
                        id={channel.id}
                        checked={formData.posting_channels.includes(channel.id)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            handleInputChange("posting_channels", [...formData.posting_channels, channel.id])
                          } else {
                            handleInputChange(
                              "posting_channels",
                              formData.posting_channels.filter((c: string) => c !== channel.id),
                            )
                          }
                        }}
                      />
                      <div className="flex-1">
                        <Label htmlFor={channel.id} className="font-medium">
                          {channel.name}
                        </Label>
                        <div className="text-sm text-gray-600">{channel.cost === 0 ? "Free" : `$${channel.cost}`}</div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium mb-2">Posting Summary</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Selected Channels:</span>
                      <div className="font-semibold">{formData.posting_channels.length}</div>
                    </div>
                    <div>
                      <span className="text-gray-600">Total Cost:</span>
                      <div className="font-semibold">
                        $
                        {availableChannels
                          .filter((c) => formData.posting_channels.includes(c.id))
                          .reduce((sum, c) => sum + c.cost, 0)
                          .toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Est. Reach:</span>
                      <div className="font-semibold">10,000+ candidates</div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="flex justify-between pt-6 border-t">
            <Button variant="outline" className="flex items-center gap-2 bg-transparent">
              <Eye className="h-4 w-4" />
              Preview
            </Button>

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => handleSubmit("save")}
                disabled={submitting}>
                Save as Draft
              </Button>
              <Button onClick={() => handleSubmit("publish")}
                disabled={submitting}>
                Submit for Approval
              </Button>
            </div>
          </div>
          {submitResult && (
            <div className="mt-4">
              {submitResult.error ? (
                <span className="text-red-600">{submitResult.error}</span>
              ) : (
                <span className="text-green-600">Job submitted! ID: {submitResult.id || submitResult.job_id}</span>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
