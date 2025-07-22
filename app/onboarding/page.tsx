import { OnboardingFlow } from "@/components/onboarding/onboarding-flow"
import { getCurrentUser } from "@/lib/auth"
import { redirect } from "next/navigation"

export default async function OnboardingPage() {
  const user = await getCurrentUser()

  if (!user) {
    redirect("/")
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <OnboardingFlow user={user} />
    </div>
  )
}
