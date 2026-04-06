"use client"

import { useState, useEffect } from "react"
import { AppShell } from "@/components/layout/app-shell"
import {
  Plus, Search, Briefcase, Users, Clock, DollarSign, 
  ChevronRight, Edit, Trash2, Eye, CheckCircle
} from "lucide-react"
import Link from "next/link"

interface Job {
  id: string
  title: string
  description: string
  department: string
  salaryMin?: number
  salaryMax?: number
  status: "OPEN" | "CLOSED" | "PAUSED"
  applications: any[]
  createdAt: string
  updatedAt: string
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [filterStatus, setFilterStatus] = useState("all")
  const [showNew, setShowNew] = useState(false)

  useEffect(() => {
    const loadJobs = async () => {
      try {
        const res = await fetch("/api/talent-acquisition/jobs")
        if (res.ok) {
          const data = await res.json()
          setJobs(data.items || [])
        }
      } catch (error) {
        console.error("Failed to load jobs:", error)
      } finally {
        setLoading(false)
      }
    }
    loadJobs()
  }, [])

  const filtered = jobs.filter(j => {
    const q = search.toLowerCase()
    return (
      (j.title.toLowerCase().includes(q) || j.department.toLowerCase().includes(q)) &&
      (filterStatus === "all" || j.status === filterStatus)
    )
  })

  const createJob = async () => {
    const title = prompt("Job title:")
    if (!title) return
    const description = prompt("Job description:")
    if (!description) return
    const department = prompt("Department:")
    if (!department) return

    try {
      const res = await fetch("/api/talent-acquisition/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description, department })
      })
      if (res.ok) {
        const newJob = await res.json()
        setJobs([newJob, ...jobs])
      }
    } catch (error) {
      console.error("Failed to create job:", error)
    }
    setShowNew(false)
  }

  const deleteJob = async (jobId: string) => {
    if (!confirm("Delete this job posting?")) return
    try {
      const res = await fetch("/api/talent-acquisition/jobs", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId })
      })
      if (res.ok) {
        setJobs(jobs.filter(j => j.id !== jobId))
      }
    } catch (error) {
      console.error("Failed to delete job:", error)
    }
  }

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-zinc-800 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-zinc-400">Loading job postings...</p>
          </div>
        </div>
      </AppShell>
    )
  }

  const statusColors = {
    OPEN: "bg-emerald-500/20 text-emerald-300",
    CLOSED: "bg-zinc-500/20 text-zinc-300",
    PAUSED: "bg-amber-500/20 text-amber-300"
  }

  return (
    <AppShell>
      <div className="px-6 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Job Postings</h1>
            <p className="text-sm text-zinc-500 mt-0.5">{jobs.length} positions · Manage all openings</p>
          </div>
          <button
            onClick={createJob}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" /> New Job
          </button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 mb-6">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search jobs..."
              className="w-full pl-9 pr-3 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 placeholder:text-zinc-600 focus:border-blue-500 outline-none"
            />
          </div>
          <select
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
            className="px-3 py-1.5 text-sm rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 outline-none"
          >
            <option value="all">All Status</option>
            <option value="OPEN">Open</option>
            <option value="CLOSED">Closed</option>
            <option value="PAUSED">Paused</option>
          </select>
        </div>

        {/* Jobs table */}
        <div className="border border-zinc-800 rounded-xl overflow-hidden">
          <table className="data-table w-full">
            <thead>
              <tr className="bg-zinc-900/60">
                <th>Position</th>
                <th>Department</th>
                <th>Applications</th>
                <th>Salary</th>
                <th>Status</th>
                <th>Posted</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8">
                    <p className="text-zinc-500">No jobs found</p>
                  </td>
                </tr>
              ) : (
                filtered.map(job => (
                  <tr key={job.id}>
                    <td>
                      <div className="flex items-center gap-2">
                        <Briefcase className="w-4 h-4 text-blue-400" />
                        <div>
                          <div className="text-sm font-medium text-zinc-200">{job.title}</div>
                          <div className="text-[11px] text-zinc-600 truncate max-w-xs">{job.description.substring(0, 50)}</div>
                        </div>
                      </div>
                    </td>
                    <td className="text-sm text-zinc-400">{job.department}</td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <Users className="w-3.5 h-3.5 text-zinc-600" />
                        <span className="text-sm">{job.applications?.length || 0}</span>
                      </div>
                    </td>
                    <td className="text-sm text-zinc-400">
                      {job.salaryMin && job.salaryMax
                        ? `$${(job.salaryMin / 1000).toFixed(0)}k - $${(job.salaryMax / 1000).toFixed(0)}k`
                        : "—"}
                    </td>
                    <td>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${statusColors[job.status]}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="text-xs text-zinc-600">
                      {new Date(job.createdAt).toLocaleDateString()}
                    </td>
                    <td onClick={e => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/dashboard/jobs/${job.id}`}
                          className="p-1.5 text-zinc-600 hover:text-white transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => deleteJob(job.id)}
                          className="p-1.5 text-zinc-600 hover:text-red-400 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  )
}
