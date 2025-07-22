"use client"

import { useState, useEffect } from "react"
import { User } from "@/types/user"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { MoreHorizontal, Pencil, Trash2, User as UserIcon } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { Skeleton } from "@/components/ui/skeleton"

export function UserList() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()
  const router = useRouter()

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true)
        const response = await fetch("/api/users")
        if (!response.ok) {
          throw new Error("Failed to fetch users")
        }
        const data = await response.json()
        setUsers(data)
      } catch (err) {
        console.error("Error fetching users:", err)
        setError("Failed to load users. Please try again later.")
        toast({
          title: "Error",
          description: "Failed to load users. Please try again.",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [toast])

  const handleDelete = async (userId: string) => {
    if (!confirm("Are you sure you want to delete this user?")) return
    
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: "DELETE",
      })
      
      if (!response.ok) {
        throw new Error("Failed to delete user")
      }
      
      setUsers(users.filter(user => user.id !== userId))
      toast({
        title: "Success",
        description: "User has been deleted successfully.",
      })
    } catch (err) {
      console.error("Error deleting user:", err)
      toast({
        title: "Error",
        description: "Failed to delete user. Please try again.",
        variant: "destructive",
      })
    }
  }

  const getRoleBadge = (role: string) => {
    const roleConfig = {
      admin: { label: "Admin", variant: "default" as const },
      manager: { label: "Manager", variant: "secondary" as const },
      hr: { label: "HR", variant: "outline" as const },
      employee: { label: "Employee", variant: "outline" as const },
    }

    const config = roleConfig[role as keyof typeof roleConfig] || { label: role, variant: "outline" as const }
    
    return (
      <Badge variant={config.variant}>
        {config.label}
      </Badge>
    )
  }

  if (loading) {
    return (
      <div className="space-y-4 p-4">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">{error}</p>
        <Button 
          variant="outline" 
          className="mt-4"
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </div>
    )
  }

  if (users.length === 0) {
    return (
      <div className="p-8 text-center">
        <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating a new user.</p>
        <div className="mt-6">
          <Button asChild>
            <a href="/dashboard/users/new">
              <Plus className="mr-2 h-4 w-4" />
              Add User
            </a>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Role</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Last Active</TableHead>
          <TableHead className="w-[50px]"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <TableRow key={user.id}>
            <TableCell className="font-medium">
              <div className="flex items-center">
                <div className="h-10 w-10 flex-shrink-0 rounded-full bg-gray-200 flex items-center justify-center">
                  <UserIcon className="h-5 w-5 text-gray-500" />
                </div>
                <div className="ml-4">
                  <div className="font-medium text-gray-900">
                    {user.name}
                  </div>
                  <div className="text-sm text-gray-500">
                    {user.department || 'No department'}
                  </div>
                </div>
              </div>
            </TableCell>
            <TableCell>{user.email}</TableCell>
            <TableCell>{getRoleBadge(user.role)}</TableCell>
            <TableCell>
              <div className="flex items-center">
                <span className={`h-2.5 w-2.5 rounded-full mr-2 ${user.status === 'active' ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                {user.status?.charAt(0).toUpperCase() + user.status?.slice(1) || 'Inactive'}
              </div>
            </TableCell>
            <TableCell>
              {user.lastActiveAt 
                ? new Date(user.lastActiveAt).toLocaleDateString() 
                : 'Never'}
            </TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-8 w-8 p-0">
                    <span className="sr-only">Open menu</span>
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem 
                    onClick={() => router.push(`/dashboard/users/${user.id}`)}
                    className="cursor-pointer"
                  >
                    <Pencil className="mr-2 h-4 w-4" />
                    <span>Edit</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleDelete(user.id)}
                    className="text-red-600 cursor-pointer"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    <span>Delete</span>
                  </DropdownMenuItem>
                </DropdownContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
