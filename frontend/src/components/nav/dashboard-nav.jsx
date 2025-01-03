'use client'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Menu } from "lucide-react"
import Link from 'next/link'
import { ThemeToggle } from '@/components/theme-toggle'
import { useUser } from '@/hooks/use-user'

const DashboardNav = () => {
  const router = useRouter()
  const {  logout } = useAuth()
  const { user } = useUser()

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  const navigationItems = [
    {
      title: "Dashboard",
      items: [
        {
          title: "Chat",
          href: "/chat",
          description: "Start a new chat conversation"
        },
        {
          title: "History",
          href: "/history",
          description: "View your chat history"
        },
      ]
    },
    {
      title: "Account",
      items: [
        {
          title: "Profile",
          href: "/profile",
          description: "Manage your account settings"
        },
        {
          title: "Search",
          href: "/",
          description: "Search for users and PDFs"
        },
      ]
    }
  ]

  // Add admin-specific items if user is admin
  if (user?.role === 'ADMIN') {
    navigationItems.push({
      title: "Admin",
      items: [
        {
          title: "Admin Dashboard",
          href: "/admin",
          description: "View admin dashboard"
        },
        {
          title: "Create Admin",
          href: "/admin/create",
          description: "Create new admin users"
        }
      ]
    })
  }

  return (
    <div className="border-b">
      <div className="flex h-16 items-center px-4 container mx-auto">
        {/* Mobile Navigation Drawer */}
        {user && <Sheet>
          <SheetTrigger asChild className="lg:hidden">
            <Button variant="ghost" size="icon">
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left">
            <SheetHeader>
              <SheetTitle>Menu</SheetTitle>
              <SheetDescription>
                {user.name}
              </SheetDescription>
            </SheetHeader>
            <div className="flex flex-col gap-4 mt-4">
              {navigationItems.map((section) => (
                <div key={section.title} className="space-y-2">
                  <h3 className="font-medium text-sm">{section.title}</h3>
                  {section.items.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="block px-2 py-1 text-sm rounded-md hover:bg-accent"
                    >
                      {item.title}
                    </Link>
                  ))}
                </div>
              ))}

            </div>
          </SheetContent>
        </Sheet>}

        {/* Desktop Navigation Menu */}
        <div className="hidden lg:flex lg:flex-1">
          {user && <NavigationMenu>
            <NavigationMenuList>
              {navigationItems.map((section) => (
                <NavigationMenuItem key={section.title}>
                  <NavigationMenuTrigger>{section.title}</NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2">
                      {section.items.map((item) => (
                        <li key={item.href}>
                          <NavigationMenuLink asChild>
                            <Link
                              href={item.href}
                              className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                            >
                              <div className="text-sm font-medium leading-none">
                                {item.title}
                              </div>
                              <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                                {item.description}
                              </p>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                      ))}
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>}
        </div>

        {/* Right side buttons */}
        <div className="ml-auto flex items-center space-x-4">
          <ThemeToggle />
          {user && <Button onClick={handleLogout} variant="ghost">
            Logout
          </Button>}
        </div>
      </div>
    </div>
  )
}

export default DashboardNav 