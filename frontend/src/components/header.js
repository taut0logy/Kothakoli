import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"
import { AuthButton } from "@/components/auth-button"
import { Button } from "@/components/ui/button"
import { History } from "lucide-react"

// Client component for navigation
function Navigation({ user }) {
  return (
    <nav className="flex items-center space-x-2">
      <AuthButton />
      <ThemeToggle />
    </nav>
  );
}

// Server component for header
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center mx-auto px-4 justify-between">
        <div className="mr-4 flex justify-center">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold sm:inline-block">
              Kothakoli
            </span>
          </Link>
        </div>
        <div className="flex flex-1 items-center space-x-2 justify-end">
          <Navigation />
        </div>
      </div>
    </header>
  )
} 