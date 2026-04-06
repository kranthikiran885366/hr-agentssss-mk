"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import {
  LayoutDashboard, Users, MessageSquare, TrendingUp,
  FileText, Settings, LogOut, Zap, ChevronRight,
  GitBranch, UserCheck, BarChart3, Bell, Search,
  Activity, Briefcase, Calendar, Shield
} from "lucide-react"

const NAV_SECTIONS = [
  {
    label: "Core",
    items: [
      { href: "/dashboard",              icon: LayoutDashboard, label: "Command Center" },
      { href: "/dashboard/pipeline",     icon: GitBranch,       label: "Talent Pipeline" },
      { href: "/interviews",             icon: MessageSquare,   label: "Interviews" },
    ]
  },
  {
    label: "People",
    items: [
      { href: "/onboarding",             icon: UserCheck,       label: "Onboarding" },
      { href: "/dashboard/performance",  icon: TrendingUp,      label: "Performance" },
      { href: "/dashboard/users",        icon: Users,           label: "Employees" },
    ]
  },
  {
    label: "Intelligence",
    items: [
      { href: "/reports",                icon: BarChart3,       label: "Analytics" },
      { href: "/demo",                   icon: Zap,             label: "AI Demo" },
    ]
  }
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  const isActive = (href: string) =>
    pathname === href || (href !== "/dashboard" && pathname.startsWith(href))

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-4 border-b border-[hsl(var(--sidebar-border))]">
        <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
          <Zap className="w-4 h-4 text-white" />
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-sm font-bold text-white tracking-tight">HRAgent</span>
          <span className="text-[10px] text-zinc-500 font-medium uppercase tracking-widest">AI System</span>
        </div>
      </div>

      {/* Search */}
      <div className="px-3 py-2.5">
        <button className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-[hsl(240_5%_11%)] text-zinc-500 text-xs hover:bg-[hsl(240_5%_14%)] transition-colors">
          <Search className="w-3 h-3" />
          <span>Search...</span>
          <span className="ml-auto text-[10px] bg-zinc-800 px-1 py-0.5 rounded">⌘K</span>
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-1 overflow-y-auto">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label} className="mb-4">
            <p className="px-2 py-1 text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
              {section.label}
            </p>
            {section.items.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2.5 px-2.5 py-2 rounded-md text-sm mb-0.5 transition-colors ${
                    active
                      ? "bg-blue-600/15 text-blue-400 font-medium"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"
                  }`}
                >
                  <Icon className={`w-4 h-4 flex-shrink-0 ${active ? "text-blue-400" : "text-zinc-500"}`} />
                  {item.label}
                  {active && <ChevronRight className="w-3 h-3 ml-auto text-blue-400/60" />}
                </Link>
              )
            })}
          </div>
        ))}
      </nav>

      {/* Agent Status */}
      <div className="px-3 py-2 border-t border-[hsl(var(--sidebar-border))]">
        <div className="px-2 py-2 rounded-md bg-[hsl(240_5%_8%)]">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
              Agents
            </span>
            <span className="agent-live text-[10px] text-emerald-400 font-medium">Live</span>
          </div>
          <div className="space-y-1">
            {[
              { name: "Resume AI",    status: "ready" },
              { name: "Interview AI", status: "ready" },
              { name: "Onboard AI",   status: "ready" },
            ].map(a => (
              <div key={a.name} className="flex items-center justify-between">
                <span className="text-[11px] text-zinc-500">{a.name}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* User */}
      <div className="px-3 py-3 border-t border-[hsl(var(--sidebar-border))]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
            A
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-zinc-300 truncate">Admin User</p>
            <p className="text-[10px] text-zinc-600 truncate">HR Manager</p>
          </div>
          <Link href="/api/auth/signout" className="text-zinc-600 hover:text-zinc-300 transition-colors">
            <LogOut className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </aside>
  )
}
