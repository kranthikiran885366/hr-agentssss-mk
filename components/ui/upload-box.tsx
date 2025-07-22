"use client"

import type React from "react"

import { safeToLowerCase } from "@/lib/utils"
import { useState } from "react"

interface UploadBoxProps {
  onFileUploaded: (file: File) => void
}

const UploadBox: React.FC<UploadBoxProps> = ({ onFileUploaded }) => {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    handleFiles(files)
  }

  const handleFiles = (files: File[]) => {
    if (files.length === 0) return

    const file = files[0]

    const maxSizeMB = 10
    if (file.size > maxSizeMB * 1024 * 1024) {
      alert(`File size exceeds ${maxSizeMB}MB`)
      return
    }

    const allowedMimeTypes = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    const allowedExtensions = ["jpg", "jpeg", "png", "gif", "pdf"]

    const ext = safeToLowerCase(file.name.split(".").pop())
    const mime = safeToLowerCase(file.type)

    if (!allowedMimeTypes.includes(mime) && !allowedExtensions.includes(ext)) {
      alert("Invalid file type. Allowed types: JPG, JPEG, PNG, GIF, PDF")
      return
    }

    onFileUploaded(file)
  }

  return (
    <div
      className={`upload-box ${isDragging ? "dragging" : ""}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <label htmlFor="file-input" className="upload-label">
        {isDragging ? "Drop here!" : "Drag & drop files or browse"}
      </label>
      <input id="file-input" type="file" className="hidden" onChange={handleFileInputChange} />
    </div>
  )
}

export { UploadBox }
