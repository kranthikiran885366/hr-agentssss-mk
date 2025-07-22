import { Button } from "@/components/ui/button"
import { useState } from "react"

export function BenefitsEnrollmentStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [benefits, setBenefits] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/benefits-enrollment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, benefits: benefits.split(",").map(b => b.trim()) })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to enroll benefits")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Benefits Enrollment</h2>
      <p className="mb-4">Enroll in your benefits (health, dental, etc.).</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter benefits, comma separated"
        value={benefits}
        onChange={e => setBenefits(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !benefits}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 