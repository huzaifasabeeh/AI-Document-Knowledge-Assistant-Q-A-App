"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { FileText } from "lucide-react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-[#F6F8F7] dark:bg-[#10221F]">
        <div className="w-11 h-11 rounded-2xl bg-[#147D65] flex items-center justify-center text-white shadow-sm animate-pulse mb-3">
          <FileText className="w-5 h-5 stroke-[2.5]" />
        </div>
        <span className="text-xs font-medium text-[#5C7069] dark:text-[#94A7A1]">
          Verifying session…
        </span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
