import { Button } from "@/components/ui/button"
import { useState } from "react"

export function BuddyAssignmentStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [buddyName, setBuddyName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/buddy-assignment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, buddy: { name: buddyName } })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to assign buddy")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Buddy Assignment</h2>
      <p className="mb-4">Get assigned an HR buddy for support during onboarding.</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter buddy name"
        value={buddyName}
        onChange={e => setBuddyName(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !buddyName}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 