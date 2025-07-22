import { Button } from "@/components/ui/button"
import { useState } from "react"

export function TrainingAssignmentStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [trainings, setTrainings] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/training-assignment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, trainings: trainings.split(",").map(t => t.trim()) })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to assign training")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Training Assignment</h2>
      <p className="mb-4">Complete your assigned training modules.</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter trainings, comma separated"
        value={trainings}
        onChange={e => setTrainings(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !trainings}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 