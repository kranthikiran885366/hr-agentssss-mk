import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface DiversityReportProps {
  jobOptions: { id: string; title: string }[]
}

export function DiversityReport({ jobOptions }: DiversityReportProps) {
  const [selectedJob, setSelectedJob] = useState<string>(jobOptions[0]?.id || "")
  const [timePeriod, setTimePeriod] = useState<string>("30d")
  const [report, setReport] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchReport = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = `?diversityReport=true&jobId=${selectedJob}&time_period=${timePeriod}`
      const res = await fetch(`/api/talent-acquisition/candidates${params}`)
      const data = await res.json()
      setReport(data)
    } catch (err) {
      setError("Failed to fetch diversity report")
      setReport(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedJob) fetchReport()
    // eslint-disable-next-line
  }, [selectedJob, timePeriod])

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Diversity Report</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <Select value={selectedJob} onValueChange={setSelectedJob}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select Job" />
              </SelectTrigger>
              <SelectContent>
                {jobOptions.map((job) => (
                  <SelectItem key={job.id} value={job.id}>{job.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={timePeriod} onValueChange={setTimePeriod}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Time Period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={fetchReport} disabled={loading}>Refresh</Button>
          </div>
          {loading ? (
            <div>Loading...</div>
          ) : error ? (
            <div className="text-red-600">{error}</div>
          ) : report ? (
            <div>
              <div className="font-semibold mb-2">Key Metrics</div>
              <ul className="list-disc ml-6 mb-4">
                {Object.entries(report.metrics || {}).map(([key, value]) => (
                  <li key={key}>{key}: {value as string}</li>
                ))}
              </ul>
              <div className="font-semibold mb-2">Breakdown</div>
              <ul className="list-disc ml-6">
                {(report.breakdown || []).map((item: any, idx: number) => (
                  <li key={idx}>{item.label}: {item.value}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div>No report data.</div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 