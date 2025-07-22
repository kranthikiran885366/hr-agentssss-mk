"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { UploadBox } from "@/components/ui/upload-box"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Upload, FileText, AlertCircle, X, Loader2 } from "lucide-react"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ALLOWED_FILE_TYPES = ['application/pdf', 'image/jpeg', 'image/png']

interface UploadProgress {
  [key: string]: number
}

interface DocumentUploadStepProps {
  onNext: () => void
  onPrevious: () => void
}

interface Document {
  id: string
  name: string
  type: string
  status: "uploading" | "uploaded" | "pending" | "error"
  file?: File
  error?: string
  previewUrl?: string
}

export function DocumentUploadStep({ onNext, onPrevious }: DocumentUploadStepProps) {
  const [documents, setDocuments] = useState<Document[]>([
    { 
      id: "1", 
      name: "Government ID", 
      type: "id", 
      status: "pending",
      description: "Passport, Driver's License, or Aadhar Card (max 5MB, PDF/JPEG/PNG)"
    },
    { 
      id: "2", 
      name: "Educational Certificate", 
      type: "education", 
      status: "pending",
      description: "Degree, Diploma, or Certificate (max 5MB, PDF/JPEG/PNG)"
    },
    { 
      id: "3", 
      name: "Resume/CV", 
      type: "resume", 
      status: "pending",
      description: "Your most recent CV or Resume (max 5MB, PDF/JPEG/PNG)",
      required: true
    },
    { 
      id: "4", 
      name: "Previous Employment Letter", 
      type: "employment", 
      status: "pending",
      description: "Previous employment verification (optional, max 5MB, PDF/JPEG/PNG)",
      required: false
    },
  ])

  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validateFile = (file: File, documentId: string): { valid: boolean; error?: string } => {
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: 'File size exceeds 5MB limit' }
    }
    
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Please upload PDF, JPEG, or PNG' }
    }
    
    return { valid: true }
  }

  const simulateUpload = useCallback((documentId: string, file: File): Promise<void> => {
    return new Promise((resolve, reject) => {
      let progress = 0
      const interval = setInterval(() => {
        progress += Math.random() * 20
        if (progress >= 100) {
          clearInterval(interval)
          resolve()
        }
        setUploadProgress(prev => ({
          ...prev,
          [documentId]: Math.min(progress, 100)
        }))
      }, 200)
    })
  }, [])

  const handleFileUpload = async (documentId: string, file: File) => {
    const doc = documents.find(d => d.id === documentId)
    if (!doc) return

    const { valid, error } = validateFile(file, documentId)
    
    if (!valid) {
      setDocuments(docs =>
        docs.map(doc => 
          doc.id === documentId 
            ? { ...doc, status: 'error' as const, error }
            : doc
        )
      )
      toast.error(`Upload failed: ${error}`)
      return
    }

    try {
      // Update document state to uploading
      setDocuments(docs =>
        docs.map(doc => 
          doc.id === documentId 
            ? { 
                ...doc, 
                status: 'uploading' as const, 
                file,
                previewUrl: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
              }
            : doc
        )
      )

      // Simulate upload with progress
      await simulateUpload(documentId, file)
      
      // Update to uploaded state
      setDocuments(docs =>
        docs.map(doc => 
          doc.id === documentId 
            ? { ...doc, status: 'uploaded' as const }
            : doc
        )
      )
      
      toast.success(`${doc.name} uploaded successfully`)
    } catch (error) {
      console.error('Upload error:', error)
      setDocuments(docs =>
        docs.map(doc => 
          doc.id === documentId 
            ? { ...doc, status: 'error' as const, error: 'Upload failed. Please try again.' }
            : doc
        )
      )
      toast.error(`Failed to upload ${doc.name}`)
    } finally {
      // Clear progress
      setUploadProgress(prev => {
        const newProgress = { ...prev }
        delete newProgress[documentId]
        return newProgress
      })
    }
  }

  const handleRemoveFile = (documentId: string) => {
    setDocuments(docs =>
      docs.map(doc => 
        doc.id === documentId 
          ? { ...doc, status: 'pending' as const, file: undefined, error: undefined }
          : doc
      )
    )
  }

  const requiredDocs = documents.filter(doc => doc.required !== false)
  const uploadedCount = documents.filter(doc => doc.status === "uploaded").length
  const requiredUploadedCount = requiredDocs.filter(doc => doc.status === "uploaded").length
  const canProceed = requiredUploadedCount === requiredDocs.length

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "uploaded":
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case "uploading":
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-600" />
      default:
        return <Upload className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "uploaded":
        return <Badge className="bg-green-100 text-green-800">Uploaded</Badge>
      case "uploading":
        return <Badge className="bg-blue-100 text-blue-800">Uploading...</Badge>
      case "error":
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      // Here you would typically submit all documents to your backend
      const formData = new FormData()
      documents.forEach(doc => {
        if (doc.file) {
          formData.append(`documents[${doc.type}]`, doc.file)
        }
      })
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.success('Documents submitted successfully')
      onNext()
    } catch (error) {
      console.error('Submission error:', error)
      toast.error('Failed to submit documents. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Upload Required Documents</CardTitle>
          <p className="text-gray-600">
            Please upload the following documents. {requiredDocs.length} required document(s) to proceed.
          </p>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Upload Progress</span>
              <span className="text-sm text-gray-600">
                {uploadedCount} of {documents.length} files uploaded
                {requiredDocs.length > 0 && ` (${requiredUploadedCount}/${requiredDocs.length} required)`}
              </span>
            </div>
            <Progress 
              value={(requiredUploadedCount / Math.max(1, requiredDocs.length)) * 100} 
              className="h-2"
            />
          </div>

          <div className="space-y-4">
            {documents.map((document) => (
              <div 
                key={document.id} 
                className={cn(
                  "border rounded-lg p-4 transition-all",
                  document.status === 'error' ? 'border-red-200 bg-red-50' : 'border-gray-200',
                  document.required === false && 'opacity-80'
                )}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start space-x-3">
                    {getStatusIcon(document.status)}
                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium">{document.name}</h3>
                        {document.required === false && (
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                            Optional
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {document.description}
                      </p>
                      {document.error && (
                        <p className="text-sm text-red-600 mt-1">{document.error}</p>
                      )}
                    </div>
                  </div>
                  {getStatusBadge(document.status)}
                </div>

                {document.status === 'uploading' && uploadProgress[document.id] && (
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Uploading...</span>
                      <span>{Math.round(uploadProgress[document.id])}%</span>
                    </div>
                    <Progress value={uploadProgress[document.id]} className="h-2" />
                  </div>
                )}

                {document.status === "uploaded" ? (
                  <div className="mt-2">
                    <div className="flex items-center justify-between bg-gray-50 rounded-md p-3">
                      <div className="flex items-center space-x-2">
                        <FileText className="h-5 w-5 text-gray-500" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                            {document.file?.name || "Document uploaded"}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(document.file?.size || 0) > 0 
                              ? `${(document.file!.size / 1024 / 1024).toFixed(1)} MB` 
                              : 'Size not available'}
                          </p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        {document.previewUrl && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(document.previewUrl, '_blank')}
                          >
                            Preview
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveFile(document.id)}
                          className="text-red-600 hover:bg-red-50"
                        >
                          <X className="h-4 w-4 mr-1" />
                          Remove
                        </Button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="mt-2">
                    <UploadBox
                      onFileSelected={(file) => handleFileUpload(document.id, file)}
                      accept=".pdf,.jpg,.jpeg,.png"
                      maxSize={MAX_FILE_SIZE}
                      disabled={document.status === 'uploading'}
                    />
                    <p className="mt-2 text-xs text-gray-500">
                      Accepted formats: PDF, JPG, PNG (max 5MB)
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {uploadedCount > 0 && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-blue-900">Upload Successful</h3>
                  <p className="text-blue-700 text-sm mt-1">
                    Your documents have been uploaded successfully. They will be verified in the next step.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex flex-col items-start space-y-4 pt-6 border-t">
          <div className="w-full space-y-2">
            <h4 className="text-sm font-medium">Tips for uploading documents:</h4>
            <ul className="text-sm text-gray-600 space-y-1 list-disc pl-5">
              <li>Ensure all text is clear and readable</li>
              <li>Files should not be password protected</li>
              <li>Check that all pages of multi-page documents are included</li>
              <li>Make sure documents are not expired</li>
            </ul>
          </div>
        </CardFooter>
      </Card>

      <div className="flex justify-between items-center pt-4">
        <Button 
          variant="outline" 
          onClick={onPrevious}
          disabled={isSubmitting}
        >
          Back
        </Button>
        <div className="flex items-center space-x-3">
          {!canProceed && (
            <p className="text-sm text-gray-500">
              {requiredUploadedCount} of {requiredDocs.length} required documents uploaded
            </p>
          )}
          <Button 
            onClick={handleSubmit}
            disabled={!canProceed || isSubmitting}
            className="min-w-[120px]"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : 'Continue'}
          </Button>
        </div>
      </div>
    </div>
  )
}
