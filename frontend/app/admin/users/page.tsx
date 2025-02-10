import { Metadata } from "next";
import { Users } from "@/components/admin/Users";
import { Separator } from "@/components/ui/separator";

export const metadata: Metadata = {
  title: "Users | Admin Dashboard",
  description: "Manage and monitor registered users",
};

export default function UsersPage() {
  return (
    <div className="space-y-6 p-6 pb-16 block">
      <div className="space-y-0.5">
        <h2 className="text-2xl font-bold tracking-tight">Users</h2>
        <p className="text-muted-foreground">
          View and manage all registered users in the system.
        </p>
      </div>
      <Separator className="my-6" />
      <div className="flex flex-col space-y-8 lg:max-w-5xl">
        <Users />
      </div>
    </div>
  );
} 