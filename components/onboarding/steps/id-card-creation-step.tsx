import { Button } from "@/components/ui/button"
import { useState } from "react"

export function IDCardCreationStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [idCardNumber, setIdCardNumber] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/id-card-creation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, id_card: { number: idCardNumber } })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to create ID card")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">ID Card Creation</h2>
      <p className="mb-4">Generate your employee ID card.</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter ID card number"
        value={idCardNumber}
        onChange={e => setIdCardNumber(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !idCardNumber}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 