import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"

export function ExitManagementDashboard({ userId }: { userId: string }) {
  const [exitProcess, setExitProcess] = useState<any>(null)
  const [reason, setReason] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>("")
  const [step, setStep] = useState("init")
  const [notification, setNotification] = useState<string>("")

  // Poll for real-time updates
  useEffect(() => {
    let interval: any
    if (exitProcess) {
      interval = setInterval(fetchExitProcess, 5000)
    }
    return () => clearInterval(interval)
    // eslint-disable-next-line
  }, [exitProcess])

  // Fetch exit process for this user
  useEffect(() => {
    fetchExitProcess()
    // eslint-disable-next-line
  }, [])

  const fetchExitProcess = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch(`/api/exit/process?employee_id=${userId}`)
      const data = await res.json()
      if (data.success) {
        setExitProcess(data.exit_process)
      } else {
        setExitProcess(null)
      }
    } catch (e) {
      setExitProcess(null)
    } finally {
      setLoading(false)
    }
  }

  const initiateResignation = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/exit/resignation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ employee_id: userId, reason })
      })
      const data = await res.json()
      if (data.success) {
        setExitProcess({ id: data.exit_id, status: "initiated", steps: { resignation: "completed" } })
        setStep("track")
        setNotification("Resignation submitted successfully.")
      } else {
        setError(data.message || "Failed to initiate resignation")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  // Step: Schedule Exit Interview
  const [interviewDate, setInterviewDate] = useState("")
  const scheduleInterview = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/exit/interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exit_id: exitProcess.id, scheduled_at: interviewDate })
      })
      const data = await res.json()
      if (data.success) {
        setNotification("Exit interview scheduled.")
        fetchExitProcess()
      } else {
        setError(data.message || "Failed to schedule interview")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  // Step: Submit Exit Feedback
  const [feedback, setFeedback] = useState("")
  const submitFeedback = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/exit/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exit_id: exitProcess.id, feedback: { text: feedback } })
      })
      const data = await res.json()
      if (data.success) {
        setNotification("Exit feedback submitted.")
        fetchExitProcess()
      } else {
        setError(data.message || "Failed to submit feedback")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  // Step: Update Clearance Checklist
  const [clearance, setClearance] = useState("")
  const updateClearance = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/exit/clearance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exit_id: exitProcess.id, checklist: clearance.split(",").map(c => c.trim()) })
      })
      const data = await res.json()
      if (data.success) {
        setNotification("Clearance checklist updated.")
        fetchExitProcess()
      } else {
        setError(data.message || "Failed to update clearance")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  // Step: Process Final Settlement
  const [settlement, setSettlement] = useState("")
  const processSettlement = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/exit/final-settlement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exit_id: exitProcess.id, settlement: { details: settlement } })
      })
      const data = await res.json()
      if (data.success) {
        setNotification("Final settlement processed.")
        fetchExitProcess()
      } else {
        setError(data.message || "Failed to process settlement")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  // Step: Generate/Download Exit Documents
  const [documents, setDocuments] = useState("")
  const generateDocuments = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/exit/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exit_id: exitProcess.id, documents: documents.split(",").map(d => d.trim()) })
      })
      const data = await res.json()
      if (data.success) {
        setNotification("Exit documents generated.")
        fetchExitProcess()
      } else {
        setError(data.message || "Failed to generate documents")
      }
    } catch (e) {
      setError("Network error")
    } finally {
      setLoading(false)
    }
  }

  if (!exitProcess && step === "init") {
    return (
      <div className="max-w-xl mx-auto p-6">
        <h2 className="text-2xl font-bold mb-4">Initiate Resignation</h2>
        <input
          className="border p-2 rounded w-full mb-2"
          placeholder="Reason for resignation"
          value={reason}
          onChange={e => setReason(e.target.value)}
          disabled={loading}
        />
        {error && typeof error === "string" && <div className="text-red-500 mb-2">{error}</div>}
        {notification && typeof notification === "string" && <div className="text-green-600 mb-2">{notification}</div>}
        <Button onClick={initiateResignation} disabled={loading || !reason}>
          {loading ? "Submitting..." : "Submit Resignation"}
        </Button>
      </div>
    )
  }

  if (exitProcess) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <h2 className="text-2xl font-bold mb-4">Exit Process Tracker</h2>
        {notification && typeof notification === "string" && <div className="text-green-600 mb-2">{notification}</div>}
        <div className="mb-4">
          <div>Status: <span className="font-semibold">{exitProcess.status}</span></div>
          <div>Steps:</div>
          <ul className="list-disc ml-6">
            {Object.entries(exitProcess.steps || {}).map(([k, v]) => (
              <li key={k}>{k}: <span className="font-semibold">{v}</span></li>
            ))}
          </ul>
        </div>
        {/* Schedule Exit Interview */}
        <div className="mb-4">
          <h3 className="font-semibold">Schedule Exit Interview</h3>
          <input
            className="border p-2 rounded w-full mb-2"
            type="datetime-local"
            value={interviewDate}
            onChange={e => setInterviewDate(e.target.value)}
            disabled={loading}
          />
          <Button onClick={scheduleInterview} disabled={loading || !interviewDate} className="mb-2">Schedule Interview</Button>
        </div>
        {/* Submit Exit Feedback */}
        <div className="mb-4">
          <h3 className="font-semibold">Submit Exit Feedback</h3>
          <textarea
            className="border p-2 rounded w-full mb-2"
            placeholder="Your feedback..."
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            disabled={loading}
          />
          <Button onClick={submitFeedback} disabled={loading || !feedback} className="mb-2">Submit Feedback</Button>
        </div>
        {/* Update Clearance Checklist */}
        <div className="mb-4">
          <h3 className="font-semibold">Update Clearance Checklist</h3>
          <input
            className="border p-2 rounded w-full mb-2"
            placeholder="Comma separated items (e.g., Laptop, ID Card, Access Card)"
            value={clearance}
            onChange={e => setClearance(e.target.value)}
            disabled={loading}
          />
          <Button onClick={updateClearance} disabled={loading || !clearance} className="mb-2">Update Clearance</Button>
        </div>
        {/* Process Final Settlement */}
        <div className="mb-4">
          <h3 className="font-semibold">Process Final Settlement (F&F)</h3>
          <input
            className="border p-2 rounded w-full mb-2"
            placeholder="Settlement details"
            value={settlement}
            onChange={e => setSettlement(e.target.value)}
            disabled={loading}
          />
          <Button onClick={processSettlement} disabled={loading || !settlement} className="mb-2">Process Settlement</Button>
        </div>
        {/* Generate/Download Exit Documents */}
        <div className="mb-4">
          <h3 className="font-semibold">Generate Exit Documents</h3>
          <input
            className="border p-2 rounded w-full mb-2"
            placeholder="Comma separated document names (e.g., Relieving Letter, Experience Letter)"
            value={documents}
            onChange={e => setDocuments(e.target.value)}
            disabled={loading}
          />
          <Button onClick={generateDocuments} disabled={loading || !documents} className="mb-2">Generate Documents</Button>
        </div>
      </div>
    )
  }

  return null
} 