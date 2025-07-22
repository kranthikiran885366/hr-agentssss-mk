import { Button } from "@/components/ui/button"
import { useState } from "react"

export function PolicyAcknowledgmentStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/policy-acknowledgment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, acknowledged: true })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to acknowledge policy")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Policy Acknowledgment</h2>
      <p className="mb-4">Acknowledge company policies to proceed.</p>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 