'use client';

import { useState } from 'react';
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  History,
  Bookmark,
  Bell,
  Settings,
  Menu,
  X,
  ShieldCheck
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface NavItem {
  title: string;
  href: string;
  icon: any;
}

const navItems: NavItem[] = [
  {
    title: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "History",
    href: "/dashboard/history",
    icon: History,
  },
  {
    title: "Saved Items",
    href: "/dashboard/saved",
    icon: Bookmark,
  },
];

export default function DashboardLayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Sidebar Toggle */}
      <button
        className="fixed p-2 bg-background border rounded-lg shadow-lg md:hidden z-50 top-4 left-4"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
      >
        {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 bg-background border-r transition-transform duration-200 ease-in-out",
          isSidebarOpen ? "translate-x-0" : "-translate-x-full",
          "md:translate-x-0"
        )}
      >
        <div className="flex flex-col h-full">
          <div className="p-6">
            <h1 className="text-2xl font-bold">Dashboard</h1>
          </div>

          <nav className="flex-1 p-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors",
                    window.location.pathname === item.href && "bg-muted text-foreground"
                  )}
                >
                  <Icon size={20} />
                  <span>{item.title}</span>
                </a>
              );
            })}

            <div className="pt-4 mt-4 border-t bg-background">
              <a
                href="/admin/dashboard"
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-primary hover:text-primary hover:bg-primary/10 transition-colors"
              >
                <ShieldCheck size={20} />
                <span className="font-semibold">CRE Admin Panel</span>
              </a>
            </div>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className={cn(
        "transition-all duration-200 ease-in-out",
        isSidebarOpen ? "md:ml-64" : "md:ml-0"
      )}>
        <main className="p-8">{children}</main>
      </div>

      
    </div>
  );

} 