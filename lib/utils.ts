import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Safe toLowerCase helper to prevent undefined errors
export function safeToLowerCase(str: string | undefined | null): string {
  return str?.toLowerCase() || ""
}

// Format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
  }).format(amount)
}

// Format date
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-IN").format(new Date(date))
}

// Calculate days between dates
export function daysBetween(start: Date, end: Date): number {
  const diffTime = Math.abs(end.getTime() - start.getTime())
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

// Generate unique ID
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}
