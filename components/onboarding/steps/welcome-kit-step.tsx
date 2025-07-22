import { Button } from "@/components/ui/button"
import { useState } from "react"

export function WelcomeKitStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [kitDesc, setKitDesc] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/welcome-kit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, kit: { description: kitDesc } })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to send welcome kit")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Welcome Kit</h2>
      <p className="mb-4">Receive your welcome kit with company materials and gifts.</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter welcome kit description"
        value={kitDesc}
        onChange={e => setKitDesc(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !kitDesc}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 