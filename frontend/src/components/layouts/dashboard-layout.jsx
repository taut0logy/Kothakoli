import DashboardNav from '@/components/nav/dashboard-nav'

const DashboardLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-background">
      <DashboardNav />
      <main className="container mx-auto py-6 px-4">
        {children}
      </main>
    </div>
  )
}

export default DashboardLayout 