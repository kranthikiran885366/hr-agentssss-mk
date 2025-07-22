import { UserList } from "@/components/users/user-list"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { redirect } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import Link from "next/link"

export default async function UsersPage() {
  const session = await getServerSession(authOptions)
  
  // Redirect if not authenticated or not an admin
  if (!session?.user) {
    redirect("/auth/signin")
  }
  
  // Check if user has admin role
  const isAdmin = session.user.role === 'admin'
  
  if (!isAdmin) {
    redirect("/dashboard")
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">User Management</h1>
          <p className="text-muted-foreground">
            Manage system users, roles, and permissions
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/users/new">
            <Plus className="mr-2 h-4 w-4" />
            Add User
          </Link>
        </Button>
      </div>
      
      <div className="rounded-md border">
        <UserList />
      </div>
    </div>
  )
}
