import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

interface JobRequisition {
  id: string
  title: string
  department: string
  location: string
  employment_type: string
  experience_level: string
  description: string
  approvers: string[]
  approval_status: string
  approval_history: any[]
}

export function RequisitionApproval() {
  const [requisitions, setRequisitions] = useState<JobRequisition[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [comment, setComment] = useState<{ [id: string]: string }>({})
  const [result, setResult] = useState<{ [id: string]: string }>({})

  const fetchRequisitions = async () => {
    setLoading(true)
    try {
      const res = await fetch("/api/talent-acquisition/jobs?pending=true")
      const data = await res.json()
      setRequisitions(data)
    } catch (error) {
      setRequisitions([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRequisitions()
  }, [])

  const handleAction = async (id: string, action: "approve" | "reject") => {
    setActionLoading(id)
    setResult({})
    try {
      const res = await fetch("/api/talent-acquisition/jobs", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId: id, approverId: "admin", action, comment: comment[id] || "" }),
      })
      const data = await res.json()
      setResult((prev) => ({ ...prev, [id]: data.status || data.error }))
      fetchRequisitions()
    } catch (error) {
      setResult((prev) => ({ ...prev, [id]: "Failed to update requisition" }))
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Pending Job Requisitions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div>Loading...</div>
          ) : requisitions.length === 0 ? (
            <div>No pending requisitions.</div>
          ) : (
            <div className="space-y-4">
              {requisitions.map((req) => (
                <div key={req.id} className="border rounded p-4 space-y-2">
                  <div className="font-semibold">{req.title} ({req.department})</div>
                  <div className="text-sm text-gray-600">{req.location} | {req.employment_type} | {req.experience_level}</div>
                  <div className="text-sm">{req.description}</div>
                  <Textarea
                    placeholder="Comment (optional)"
                    value={comment[req.id] || ""}
                    onChange={e => setComment((prev) => ({ ...prev, [req.id]: e.target.value }))}
                    className="mt-2"
                  />
                  <div className="flex gap-2 mt-2">
                    <Button size="sm" onClick={() => handleAction(req.id, "approve")} disabled={actionLoading === req.id}>Approve</Button>
                    <Button size="sm" variant="destructive" onClick={() => handleAction(req.id, "reject")} disabled={actionLoading === req.id}>Reject</Button>
                  </div>
                  {result[req.id] && (
                    <div className={result[req.id] === "approved" ? "text-green-600" : "text-red-600"}>{result[req.id]}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 