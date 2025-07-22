import { Button } from "@/components/ui/button"
import { useState } from "react"

export function CompletionCertificationStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [certificateId, setCertificateId] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/completion-certification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, certificate: { id: certificateId } })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to issue certificate")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Completion Certification</h2>
      <p className="mb-4">Receive your onboarding completion certificate.</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter certificate ID"
        value={certificateId}
        onChange={e => setCertificateId(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !certificateId}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 