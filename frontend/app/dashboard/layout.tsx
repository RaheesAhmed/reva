import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import DashboardLayoutClient from "./layout.client";

// Server Component for Auth Check
async function AuthCheck() {
  const cookieStore = await cookies();
  const token = cookieStore.get("userToken");

  if (!token) {
    redirect("/auth");
  }
  return null;
}

// Main Layout Component (Server Component)
export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <AuthCheck />
      <DashboardLayoutClient>{children}</DashboardLayoutClient>
    </>
  );
}
