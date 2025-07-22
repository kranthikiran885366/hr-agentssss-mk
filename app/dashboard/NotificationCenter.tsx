import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Notification {
  id: number
  message: string
  type: string
  read: boolean
  created_at: string
  event_type: string
  related_entity: string | null
}

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const userId = "hr_admin" // TODO: Replace with real user id from auth

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/talent-acquisition/notifications?user_id=${userId}`)
      const data = await res.json()
      setNotifications(data)
    } catch (error) {
      setNotifications([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
    // eslint-disable-next-line
  }, [])

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Notification Center</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div>Loading...</div>
          ) : notifications.length === 0 ? (
            <div>No notifications.</div>
          ) : (
            <ul className="space-y-2">
              {notifications.map((n) => (
                <li key={n.id} className="flex items-center gap-2 border-b pb-2">
                  <Badge variant={n.read ? "secondary" : "default"}>
                    {n.event_type.replace("_", " ")}
                  </Badge>
                  <span className={n.read ? "text-gray-500" : "text-black font-semibold"}>{n.message}</span>
                  <span className="ml-auto text-xs text-gray-400">{new Date(n.created_at).toLocaleString()}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 