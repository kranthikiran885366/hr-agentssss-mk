"use client"

import { Sidebar } from "./sidebar"

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="sidebar-layout">
      <Sidebar />
      <main className="sidebar-content min-h-screen bg-[#09090B]">
        {children}
      </main>
    </div>
  )
}
