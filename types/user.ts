export interface User {
  id: string
  name: string
  email: string
  role: "admin" | "candidate" | "mentor"
  department?: string
  joinedAt?: string
  onboardingStatus?: "pending" | "in-progress" | "completed"
}

export interface Candidate extends User {
  role: "candidate"
  documents?: Document[]
  mentor?: Mentor
  onboardingStep?: number
}

export interface Mentor extends User {
  role: "mentor"
  expertise: string[]
  rating: number
  availability: string
  mentees?: Candidate[]
}

export interface Document {
  id: string
  name: string
  type: string
  status: "uploaded" | "verified" | "rejected"
  uploadedAt: string
  verifiedAt?: string
}
