import { Button } from "@/components/ui/button"
import { useState } from "react"

export function SystemAccessSetupStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [systems, setSystems] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/system-access-setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, systems: systems.split(",").map(s => s.trim()) })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to set up system access")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">System Access Setup</h2>
      <p className="mb-4">Set up your access to company systems and tools.</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter systems, comma separated"
        value={systems}
        onChange={e => setSystems(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !systems}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 