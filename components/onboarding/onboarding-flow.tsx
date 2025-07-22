"use client"

import { useState } from "react"
import { Progress } from "@/components/ui/progress"
import { StepTracker } from "@/components/ui/step-tracker"
import { WelcomeStep } from "./steps/welcome-step"
import { DocumentUploadStep } from "./steps/document-upload-step"
import { VerificationStep } from "./steps/verification-step"
import { AccountCreationStep } from "./steps/account-creation-step"
import { MentorAssignmentStep } from "./steps/mentor-assignment-step"
import { CompletionStep } from "./steps/completion-step"
import { EquipmentProvisioningStep } from "./steps/equipment-provisioning-step"
import { PolicyAcknowledgmentStep } from "./steps/policy-acknowledgment-step"
import { BenefitsEnrollmentStep } from "./steps/benefits-enrollment-step"
import { TrainingAssignmentStep } from "./steps/training-assignment-step"
import { SystemAccessSetupStep } from "./steps/system-access-setup-step"
import { WelcomeOrientationStep } from "./steps/welcome-orientation-step"
import { WorkspaceSetupStep } from "./steps/workspace-setup-step"
import { ProbationTrackingStep } from "./steps/probation-tracking-step"
import { BuddyAssignmentStep } from "./steps/buddy-assignment-step"
import { IDCardCreationStep } from "./steps/id-card-creation-step"
import { WelcomeKitStep } from "./steps/welcome-kit-step"
import { ManagerIntroductionsStep } from "./steps/manager-introductions-step"
import { PolicyESigningStep } from "./steps/policy-e-signing-step"
import { CompletionCertificationStep } from "./steps/completion-certification-step"
import type { User } from "@/types/user"

interface OnboardingFlowProps {
  user: User
}

const steps = [
  { id: 1, title: "Welcome", description: "Introduction to the process" },
  { id: 2, title: "Documents", description: "Upload required documents" },
  { id: 3, title: "Verification", description: "Document verification" },
  { id: 4, title: "Account Setup", description: "Create system accounts" },
  { id: 5, title: "Mentor Assignment", description: "Get assigned a mentor" },
  { id: 6, title: "Workspace Setup", description: "Set up your workspace" },
  { id: 7, title: "Equipment Provisioning", description: "Provision equipment (laptop, phone, etc.)" },
  { id: 8, title: "Policy Acknowledgment", description: "Acknowledge company policies" },
  { id: 9, title: "Benefits Enrollment", description: "Enroll in benefits" },
  { id: 10, title: "Training Assignment", description: "Assigned training modules" },
  { id: 11, title: "System Access Setup", description: "Set up system access" },
  { id: 12, title: "Welcome Orientation", description: "Attend welcome orientation" },
  { id: 13, title: "Probation Tracking", description: "Track probation period" },
  { id: 14, title: "Buddy Assignment", description: "Get assigned an HR buddy" },
  { id: 15, title: "ID Card Creation", description: "Generate your employee ID card" },
  { id: 16, title: "Welcome Kit", description: "Receive your welcome kit" },
  { id: 17, title: "Manager Introductions", description: "Meet your manager/team" },
  { id: 18, title: "Policy E-signing", description: "Digitally sign company policies" },
  { id: 19, title: "Completion Certification", description: "Receive onboarding certificate" },
  { id: 20, title: "Completion", description: "Onboarding complete" },
]

export function OnboardingFlow({ user }: OnboardingFlowProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [completedSteps, setCompletedSteps] = useState<number[]>([])

  const progress = (currentStep / steps.length) * 100

  const handleNextStep = () => {
    if (currentStep < steps.length) {
      setCompletedSteps([...completedSteps, currentStep])
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return <WelcomeStep user={user} onNext={handleNextStep} />
      case 2:
        return <DocumentUploadStep onNext={handleNextStep} onPrevious={handlePreviousStep} />
      case 3:
        return <VerificationStep onNext={handleNextStep} onPrevious={handlePreviousStep} />
      case 4:
        return <AccountCreationStep onNext={handleNextStep} onPrevious={handlePreviousStep} />
      case 5:
        return <MentorAssignmentStep onNext={handleNextStep} onPrevious={handlePreviousStep} />
      case 6:
        return <WorkspaceSetupStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 7:
        return <EquipmentProvisioningStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 8:
        return <PolicyAcknowledgmentStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 9:
        return <BenefitsEnrollmentStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 10:
        return <TrainingAssignmentStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 11:
        return <SystemAccessSetupStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 12:
        return <WelcomeOrientationStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 13:
        return <ProbationTrackingStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 14:
        return <BuddyAssignmentStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 15:
        return <IDCardCreationStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 16:
        return <WelcomeKitStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 17:
        return <ManagerIntroductionsStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 18:
        return <PolicyESigningStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 19:
        return <CompletionCertificationStep onNext={handleNextStep} onPrevious={handlePreviousStep} sessionId={user.id} />
      case 20:
        return <CompletionStep user={user} />
      default:
        return <WelcomeStep user={user} onNext={handleNextStep} />
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Employee Onboarding</h1>
        <p className="text-gray-600">Complete your onboarding process step by step</p>
      </div>

      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <span className="text-sm font-medium text-gray-700">
            Step {currentStep} of {steps.length}
          </span>
          <span className="text-sm text-gray-500">{Math.round(progress)}% Complete</span>
        </div>
        <Progress value={progress} className="w-full" />
      </div>

      <StepTracker steps={steps} currentStep={currentStep} completedSteps={completedSteps} />

      <div className="mt-8">{renderCurrentStep()}</div>
    </div>
  )
}
