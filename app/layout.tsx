import type React from "react"
import "./globals.css"
import { Inter } from "next/font/google"
import { Toaster } from "@/components/ui/toaster"
import { AuthProvider } from "@/components/providers/auth-provider"
import { AIProvider } from "@/components/providers/ai-provider"
import { VoiceProvider } from "@/components/providers/voice-provider"
import { Navbar } from "@/components/layout/navbar"
import { SessionProvider } from "next-auth/react"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Advanced HR Agent System",
  description: "AI-powered HR automation with voice and chat capabilities",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SessionProvider>
          <AuthProvider>
            <AIProvider>
              <VoiceProvider>
                <Navbar />
                {children}
                <Toaster />
              </VoiceProvider>
            </AIProvider>
          </AuthProvider>
        </SessionProvider>
      </body>
    </html>
  )
}
