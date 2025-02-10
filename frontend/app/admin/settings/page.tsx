"use client";


import { SystemMessage } from "@/components/admin/SystemMessage";
import { Separator } from "@/components/ui/separator";



export default function SettingsPage() {
  return (
    <div className="space-y-6 p-6 pb-16 block">
      <div className="space-y-0.5">
        <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">
          Manage your system settings and configurations.
        </p>
      </div>
      <Separator className="my-6" />
      <div className="flex flex-col space-y-8 lg:max-w-5xl">
        <div className="col-span-2 space-y-4">
          <div>
            <h3 className="text-lg font-medium">System Message</h3>
            <p className="text-sm text-muted-foreground">
              This message defines how the AI assistant behaves and what capabilities it has access to.
            </p>
          </div>
          <SystemMessage />
        </div>
        
        {/* Add more settings sections here */}
      </div>
    </div>
  );
}
