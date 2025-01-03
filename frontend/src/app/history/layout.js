import { Suspense } from 'react'

export const metadata = {
  title: 'History - StoryGen AI',
  description: 'View your generated content history',
}

function LoadingHistory() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
    </div>
  )
}

export default function HistoryLayout({ children }) {
  return (
    <div className="relative min-h-screen">
      <div className="py-8">
        <div className="container mx-auto px-4">
          <div className="mx-auto flex max-w-[980px] flex-col items-start gap-2">
            <h1 className="text-3xl font-bold leading-tight tracking-tighter md:text-4xl">
              Content History
            </h1>
            <p className="text-lg text-muted-foreground">
              View and manage your previously generated content.
            </p>
          </div>
        </div>
      </div>
      <div className="container">
        <div className="mx-auto max-w-[980px]">
          <Suspense fallback={<LoadingHistory />}>
            {children}
          </Suspense>
        </div>
      </div>
    </div>
  )
} 