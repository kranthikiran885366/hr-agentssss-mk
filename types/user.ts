export interface User {
  id: string
  name?: string
  email: string
  role: "ADMIN" | "HR" | "MANAGER" | "USER"
  department?: string
  position?: string
  phone?: string
  bio?: string
  status: string
  image?: string
  createdAt: string
  updatedAt: string
}

export interface Candidate {
  id: string
  name: string
  email: string
  phone?: string
  status: "APPLIED" | "SCREENING" | "INTERVIEW" | "OFFER" | "HIRED" | "REJECTED"
  source?: string
  score: number
  resume?: Resume
  applications?: JobApplication[]
  interviews?: InterviewSession[]
  createdAt: string
  updatedAt: string
}

export interface Resume {
  id: string
  content: string
  analysis?: Record<string, any>
  score: number
  uploadedAt: string
}

export interface Job {
  id: string
  title: string
  description: string
  department: string
  salaryMin?: number
  salaryMax?: number
  status: "OPEN" | "CLOSED" | "ON_HOLD"
  applications?: JobApplication[]
  createdAt: string
  updatedAt: string
}

export interface JobApplication {
  id: string
  jobId: string
  candidateId: string
  status: "APPLIED" | "SCREENING" | "INTERVIEW" | "OFFER" | "ACCEPTED" | "REJECTED"
  appliedAt: string
  job?: Job
  candidate?: Candidate
}

export interface InterviewSession {
  id: string
  candidateId: string
  conductorId?: string
  jobId?: string
  type: "SCREENING" | "TECHNICAL" | "BEHAVIORAL" | "FINAL"
  status: "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED"
  startTime?: string
  endTime?: string
  score: number
  feedback?: string
  recording?: string
  transcript?: string
  messages?: InterviewMessage[]
  candidate: Candidate
  conductor?: User
  createdAt: string
  updatedAt: string
}

export interface InterviewMessage {
  id: string
  sessionId: string
  role: string
  content: string
  createdAt: string
}
