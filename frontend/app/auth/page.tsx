"use "

import { AuthForm } from "@/components/auth/AuthForm";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function AuthPage() {
  // If user is already logged in, redirect to dashboard
  const cookieStore = await cookies();
  const token = cookieStore.get("userToken");

  if (token) {
    redirect("/dashboard");
  }

  return (
    <div className="container relative min-h-screen flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0">
      <div className="relative hidden h-full flex-col bg-muted p-10 text-white lg:flex dark:border-r">
        <div className="absolute inset-0 bg-blue-900" />
        <div className="relative z-20 flex items-center text-lg font-medium">
          <img src="/logo.png" alt="CRE Assistant" className="h-8 w-8 mr-2" />
          CRE Assistant
        </div>
        <div className="relative z-20 mt-auto">
          <blockquote className="space-y-2">
            <p className="text-lg">
              "CRE Assistant has revolutionized how we analyze commercial real estate opportunities. 
              The AI-powered insights have helped us make better investment decisions."
            </p>
            <footer className="text-sm">Sofia Davis, Commercial Real Estate Analyst</footer>
          </blockquote>
        </div>
      </div>
      <div className="lg:p-8">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
          <AuthForm mode="register" />
        </div>
      </div>
    </div>
  );
}
