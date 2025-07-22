import { Button } from "@/components/ui/button"
import { useState } from "react"

export function EquipmentProvisioningStep({ onNext, onPrevious, sessionId }: { onNext: () => void; onPrevious: () => void; sessionId: string }) {
  const [equipment, setEquipment] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleNext = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/onboarding/equipment-provisioning", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, equipment: equipment.split(",").map(e => e.trim()) })
      })
      const data = await res.json()
      if (data.success) {
        onNext()
      } else {
        setError(data.message || "Failed to provision equipment")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Equipment Provisioning</h2>
      <p className="mb-4">Provision your required equipment (laptop, phone, etc.).</p>
      <input
        className="border p-2 rounded w-full mb-2"
        placeholder="Enter equipment, comma separated"
        value={equipment}
        onChange={e => setEquipment(e.target.value)}
        disabled={loading}
      />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <Button variant="outline" onClick={onPrevious} disabled={loading}>Back</Button>
        <Button onClick={handleNext} disabled={loading || !equipment}>{loading ? "Saving..." : "Next"}</Button>
      </div>
    </div>
  )
} 