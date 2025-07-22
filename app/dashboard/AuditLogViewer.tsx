import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

interface AuditLog {
  id: number
  user_id: string
  action: string
  entity_type: string
  entity_id: string
  details: string
  timestamp: string
}

export function AuditLogViewer() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [entityType, setEntityType] = useState("")
  const [entityId, setEntityId] = useState("")
  const [userId, setUserId] = useState("")

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const params = [
        entityType ? `entity_type=${entityType}` : "",
        entityId ? `entity_id=${entityId}` : "",
        userId ? `user_id=${userId}` : "",
      ].filter(Boolean).join("&")
      const res = await fetch(`/api/talent-acquisition/audit-logs${params ? `?${params}` : ""}`)
      const data = await res.json()
      setLogs(data)
    } catch (error) {
      setLogs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 30000)
    return () => clearInterval(interval)
    // eslint-disable-next-line
  }, [entityType, entityId, userId])

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Audit Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input placeholder="Entity Type" value={entityType} onChange={e => setEntityType(e.target.value)} className="w-32" />
            <Input placeholder="Entity ID" value={entityId} onChange={e => setEntityId(e.target.value)} className="w-32" />
            <Input placeholder="User ID" value={userId} onChange={e => setUserId(e.target.value)} className="w-32" />
            <Button onClick={fetchLogs}>Filter</Button>
          </div>
          {loading ? (
            <div>Loading...</div>
          ) : logs.length === 0 ? (
            <div>No audit logs found.</div>
          ) : (
            <table className="w-full text-sm border">
              <thead>
                <tr className="bg-gray-100">
                  <th className="p-2 border">Timestamp</th>
                  <th className="p-2 border">User</th>
                  <th className="p-2 border">Action</th>
                  <th className="p-2 border">Entity Type</th>
                  <th className="p-2 border">Entity ID</th>
                  <th className="p-2 border">Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id}>
                    <td className="p-2 border">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="p-2 border">{log.user_id}</td>
                    <td className="p-2 border">{log.action}</td>
                    <td className="p-2 border">{log.entity_type}</td>
                    <td className="p-2 border">{log.entity_id}</td>
                    <td className="p-2 border">{log.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 