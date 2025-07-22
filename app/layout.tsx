import type React from "react"
import "./globals.css"
import { Inter } from "next/font/google"
import { Toaster } from "@/components/ui/toaster"
import { AuthProvider } from "@/components/providers/auth-provider"
import { AIProvider } from "@/components/providers/ai-provider"
import { VoiceProvider } from "@/components/providers/voice-provider"
import { Navbar } from "@/components/layout/navbar"
import { SessionProvider } from "next-auth/react"
import type { Metadata } from "next"
import { ThemeProvider } from "@/components/theme-provider"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "HR Agent System",
  description: "AI-powered HR automation with real agents",
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
                <ThemeProvider
                  attribute="class"
                  defaultTheme="system"
                  enableSystem
                  disableTransitionOnChange
                >
                  {children}
                </ThemeProvider>
                <Toaster />
              </VoiceProvider>
            </AIProvider>
          </AuthProvider>
        </SessionProvider>
      </body>
    </html>
  )
}