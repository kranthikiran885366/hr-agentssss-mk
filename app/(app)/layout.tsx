import { Sidebar } from "@/components/layout/sidebar"

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="sidebar-layout">
      <Sidebar />
      <main className="sidebar-content">
        {children}
      </main>
    </div>
  )
}
