import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface CandidateProfileProps {
  candidateId: string
  onClose: () => void
}

export function CandidateProfile({ candidateId, onClose }: CandidateProfileProps) {
  const [candidate, setCandidate] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const fetchCandidate = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/talent-acquisition/candidates?candidateId=${candidateId}`)
      const data = await res.json()
      setCandidate(data)
    } catch (error) {
      setCandidate(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCandidate()
    // eslint-disable-next-line
  }, [candidateId])

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full p-6 relative">
        <Button className="absolute top-2 right-2" size="sm" onClick={onClose}>Close</Button>
        {loading ? (
          <div>Loading...</div>
        ) : !candidate ? (
          <div>Candidate not found.</div>
        ) : (
          <>
            <Card>
              <CardHeader>
                <CardTitle>{candidate.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-2 text-sm text-gray-600">{candidate.email} | {candidate.phone} | {candidate.location}</div>
                <div className="mb-2">Current Position: {candidate.current_position}</div>
                <div className="mb-2">Experience: {candidate.experience_years} years</div>
                <div className="mb-2">Education: {candidate.education}</div>
                <div className="mb-2">Skills: {candidate.skills?.join(", ")}</div>
                <div className="mb-2">Match Score: {candidate.match_score}</div>
                <div className="mb-2">Resume: <a href={candidate.resume_url} target="_blank" rel="noopener noreferrer" className="underline">View Resume</a></div>
                <div className="mb-2">Current Stage: {candidate.current_stage}</div>
                <div className="mb-2">Application Date: {candidate.application_date}</div>
                <div className="mb-2">Source: {candidate.source}</div>
                <div className="mb-2">Interview Feedback: {candidate.interview_feedback || "N/A"}</div>
                <div className="mb-2">History: <pre className="bg-gray-100 p-2 rounded text-xs">{JSON.stringify(candidate.history, null, 2)}</pre></div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  )
} 