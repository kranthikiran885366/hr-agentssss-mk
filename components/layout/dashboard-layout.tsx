"use client"

import type React from "react"

import { useAuth } from "@/components/providers/auth-provider"
import { Button } from "@/components/ui/button"
import { LogOut, User, Settings, Home, FileText, Users } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">HR Agent System</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.name}</span>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex">
        <aside className="w-64 bg-white shadow-sm min-h-screen">
          <nav className="mt-8">
            <div className="px-4 space-y-2">
              <Link
                href="/dashboard"
                className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
              >
                <Home className="h-5 w-5 mr-3" />
                Dashboard
              </Link>
              {user?.role === "candidate" && (
                <Link
                  href="/onboarding"
                  className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
                >
                  <FileText className="h-5 w-5 mr-3" />
                  Onboarding
                </Link>
              )}
              {user?.role === "admin" && (
                <>
                  <Link
                    href="/admin/candidates"
                    className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    <Users className="h-5 w-5 mr-3" />
                    Candidates
                  </Link>
                  <Link
                    href="/admin/mentors"
                    className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    <User className="h-5 w-5 mr-3" />
                    Mentors
                  </Link>
                </>
              )}
              <Link href="/settings" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                <Settings className="h-5 w-5 mr-3" />
                Settings
              </Link>
            </div>
          </nav>
        </aside>

        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  )
}
