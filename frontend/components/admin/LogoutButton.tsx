"use client";

import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { logout } from "@/lib/auth";

export function LogoutButton() {
  return (
    <Button
      variant="ghost"
      size="sm"
      className="text-muted-foreground hover:text-primary"
      onClick={logout}
    >
      <LogOut className="h-4 w-4 mr-2" />
      Logout
    </Button>
  );
}
