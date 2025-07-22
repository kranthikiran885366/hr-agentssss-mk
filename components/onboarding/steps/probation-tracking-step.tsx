import { Button } from "@/components/ui/button"
import { useState } from "react"

export function ProbationTrackingStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [status, setStatus] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/probation-tracking", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, status })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to update probation status")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Probation Tracking</h2>
      <p className="mb-4">Track your probation period and status.</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter probation status (e.g., In Progress, Completed)"
        value={status}
        onChange={e => setStatus(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !status}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 