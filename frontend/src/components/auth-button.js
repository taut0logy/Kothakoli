"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { LogIn, LogOut, User, Settings } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { LoadingSpinner } from "@/components/loading-spinner";
import { useAuth } from "@/contexts/auth-context";
import { useUser } from "@/hooks/use-user";

export function AuthButton() {
  const { logout } = useAuth();
  const { user, isLoading, isError } = useUser();
  const router = useRouter();
  const [loading, setloading] = useState(false);

  const handleLogin = () => {
    router.push("/login");
  };

  const handleLogout = async () => {
    setloading(true);
    try {
      await logout();
    } finally {
      setloading(false);
    }
  };

  if (loading || isLoading) {
    return (
      <Button variant="ghost" size="sm" disabled>
        <LoadingSpinner className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <>
      {(!user || isError) && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleLogin}
          className="gap-2"
        >
          <LogIn className="h-4 w-4" />
          <span>Login</span>
        </Button>
      )}
      {user && !isError && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="gap-2">
              <User className="h-4 w-4" />
              <span className="hidden sm:block">{user?.name}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48 z-50">
            <DropdownMenuLabel className="text-sm font-semibold sm:hidden">
              {user?.name}
            </DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() => router.push("/history")}
              className="cursor-pointer"
            >
              <Settings className="h-4 w-4 mr-2" />
              History
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={handleLogout}
              className="cursor-pointer text-red-600 dark:text-red-400"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </>
  );
}
