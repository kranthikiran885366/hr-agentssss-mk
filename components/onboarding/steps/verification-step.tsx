"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Clock, AlertCircle, Shield, Zap, Eye } from "lucide-react"

interface VerificationStepProps {
  onNext: () => void
  onPrevious: () => void
}

interface VerificationResult {
  documentType: string
  status: "verifying" | "verified" | "failed" | "pending"
  confidence: number
  issues?: string[]
}

export function VerificationStep({ onNext, onPrevious }: VerificationStepProps) {
  const [verificationResults, setVerificationResults] = useState<VerificationResult[]>([
    { documentType: "Government ID", status: "pending", confidence: 0 },
    { documentType: "Educational Certificate", status: "pending", confidence: 0 },
    { documentType: "Resume/CV", status: "pending", confidence: 0 },
  ])

  const [currentlyVerifying, setCurrentlyVerifying] = useState(0)
  const [verificationComplete, setVerificationComplete] = useState(false)

  useEffect(() => {
    // Simulate verification process
    const verifyDocuments = async () => {
      for (let i = 0; i < verificationResults.length; i++) {
        setCurrentlyVerifying(i)

        // Update status to verifying
        setVerificationResults((prev) =>
          prev.map((result, index) => (index === i ? { ...result, status: "verifying" } : result)),
        )

        // Simulate verification time
        await new Promise((resolve) => setTimeout(resolve, 2000))

        // Simulate verification result
        const isSuccessful = Math.random() > 0.1 // 90% success rate
        const confidence = isSuccessful ? Math.floor(Math.random() * 20) + 80 : Math.floor(Math.random() * 30) + 40

        setVerificationResults((prev) =>
          prev.map((result, index) =>
            index === i
              ? {
                  ...result,
                  status: isSuccessful ? "verified" : "failed",
                  confidence,
                  issues: isSuccessful ? undefined : ["Document quality too low", "Unable to verify authenticity"],
                }
              : result,
          ),
        )
      }

      setVerificationComplete(true)
    }

    const timer = setTimeout(verifyDocuments, 1000)
    return () => clearTimeout(timer)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case "failed":
        return <AlertCircle className="h-5 w-5 text-red-600" />
      case "verifying":
        return <Clock className="h-5 w-5 text-blue-600 animate-spin" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "verified":
        return <Badge className="bg-green-100 text-green-800">Verified</Badge>
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      case "verifying":
        return <Badge className="bg-blue-100 text-blue-800">Verifying...</Badge>
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  const verifiedCount = verificationResults.filter((r) => r.status === "verified").length
  const failedCount = verificationResults.filter((r) => r.status === "failed").length
  const canProceed = verificationComplete && verifiedCount >= 2

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-6 w-6 text-blue-600" />
            <span>Document Verification</span>
          </CardTitle>
          <p className="text-gray-600">
            Our AI-powered system is verifying the authenticity of your uploaded documents.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
                <Zap className="h-8 w-8 text-blue-600" />
                <div>
                  <h3 className="font-medium text-blue-900">AI-Powered</h3>
                  <p className="text-sm text-blue-700">Advanced ML algorithms</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
                <Shield className="h-8 w-8 text-green-600" />
                <div>
                  <h3 className="font-medium text-green-900">Secure</h3>
                  <p className="text-sm text-green-700">Bank-level encryption</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 bg-purple-50 rounded-lg">
                <Eye className="h-8 w-8 text-purple-600" />
                <div>
                  <h3 className="font-medium text-purple-900">Accurate</h3>
                  <p className="text-sm text-purple-700">99.5% accuracy rate</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {verificationResults.map((result, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(result.status)}
                      <div>
                        <h3 className="font-medium">{result.documentType}</h3>
                        {result.status === "verified" && (
                          <p className="text-sm text-gray-600">Confidence: {result.confidence}%</p>
                        )}
                      </div>
                    </div>
                    {getStatusBadge(result.status)}
                  </div>

                  {result.status === "verifying" && (
                    <div className="space-y-2">
                      <Progress value={50} className="w-full" />
                      <p className="text-sm text-gray-600">Analyzing document...</p>
                    </div>
                  )}

                  {result.status === "failed" && result.issues && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
                      <h4 className="font-medium text-red-900 mb-2">Issues Found:</h4>
                      <ul className="text-sm text-red-700 space-y-1">
                        {result.issues.map((issue, i) => (
                          <li key={i}>• {issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.status === "verified" && (
                    <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded">
                      <p className="text-sm text-green-700">
                        Document successfully verified and meets all requirements.
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {verificationComplete && (
              <div className="p-4 bg-gray-50 border rounded-lg">
                <h3 className="font-medium mb-2">Verification Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Verified Documents:</span>
                    <span className="ml-2 font-medium text-green-600">{verifiedCount}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Failed Verifications:</span>
                    <span className="ml-2 font-medium text-red-600">{failedCount}</span>
                  </div>
                </div>
                {canProceed && (
                  <p className="text-sm text-green-600 mt-2">
                    ✓ Minimum verification requirements met. You can proceed to the next step.
                  </p>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={onNext} disabled={!canProceed}>
          {canProceed ? "Continue to Account Setup" : "Verification in Progress..."}
        </Button>
      </div>
    </div>
  )
}
