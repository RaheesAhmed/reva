import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Sidebar } from "@/components/admin/Sidebar";
import { LogoutButton } from "@/components/admin/LogoutButton";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const cookieStore = cookies();
  const adminToken = cookieStore.get("adminToken");

  if (!adminToken) {
    redirect("/admin/login");
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 hidden md:block">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      <div className="md:hidden">
        {/* Add mobile sidebar here later */}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-14 items-center justify-between">
            <div className="mr-4 flex">
              <a href="/admin/dashboard" className="mr-6 flex items-center space-x-2">
                <span className="font-bold">CRE Admin</span>
              </a>
            </div>
            <LogoutButton />
          </div>
        </header>
        <main className="container py-6">
          {children}
        </main>
      </div>
    </div>
  );
}
