import { toast as sonnerToast } from "sonner";

interface ToastOptions {
  title: string;
  description?: string;
  variant?: "default" | "destructive";
  duration?: number;
}

export default function toast({
  title,
  description,
  variant = "default",
  duration = 3000,
}: ToastOptions) {
  return sonnerToast[variant === "destructive" ? "error" : "success"](title, {
    description,
    duration,
  });
}
