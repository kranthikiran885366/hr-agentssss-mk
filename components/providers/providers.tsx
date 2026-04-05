"use client"

import { SessionProvider } from "next-auth/react"
import { AuthProvider } from "@/components/providers/auth-provider"
import { AIProvider } from "@/components/providers/ai-provider"
import { VoiceProvider } from "@/components/providers/voice-provider"
import { ThemeProvider } from "@/components/theme-provider"
import { Navbar } from "@/components/layout/navbar"
import type { ReactNode } from "react"

export function Providers({ children }: { children: ReactNode }) {
  return (
    <SessionProvider>
      <AuthProvider>
        <AIProvider>
          <VoiceProvider>
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              <Navbar />
              {children}
            </ThemeProvider>
          </VoiceProvider>
        </AIProvider>
      </AuthProvider>
    </SessionProvider>
  )
}
