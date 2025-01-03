import { Inter, Geist, Geist_Mono } from "next/font/google"
import './globals.css'
import { Toaster } from 'sonner'
import { AuthProvider } from '@/contexts/auth-context'
import DashboardLayout from '@/components/layouts/dashboard-layout'
import { ThemeProvider } from '@/components/theme-provider'

const inter = Inter({ subsets: ['latin'] })

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata = {
  title: "Kothakoli",
  description: "A general purpose AI platform capable of working with text, images, and audio and supports banglish and bangla.",
}

export default function RootLayout({ children }) {
  // List of paths that don't need the dashboard layout
  const publicPaths = ['/login', '/signup', '/forgot-password', '/reset-password']
  const isPublicPath = publicPaths.some(path => 
    typeof window !== 'undefined' && window.location.pathname.startsWith(path)
  )

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} ${geistSans.variable} ${geistMono.variable}`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            {isPublicPath ? (
              children
            ) : (
              <DashboardLayout>
                {children}
              </DashboardLayout>
            )}
            <Toaster richColors closeButton position="top-right" />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
