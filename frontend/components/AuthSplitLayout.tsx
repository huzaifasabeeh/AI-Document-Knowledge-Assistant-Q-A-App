"use client";

import React from "react";
import Link from "next/link";
import { FileText, CheckCircle2, Lock, Sun, Moon } from "lucide-react";
import { useTheme } from "@/lib/theme-context";

interface AuthSplitLayoutProps {
  children: React.ReactNode;
}

export function AuthSplitLayout({ children }: AuthSplitLayoutProps) {
  const { resolvedTheme, setTheme } = useTheme();

  return (
    <div className="min-h-screen w-screen flex flex-col lg:flex-row bg-white dark:bg-[#10221F] overflow-y-auto">
      {/* Left Brand Panel */}
      <div className="lg:w-5/12 bg-[#122A24] dark:bg-[#0C1B17] p-8 lg:p-14 text-white flex flex-col justify-between relative select-none">
        <div>
          <Link href="/login" className="inline-flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#147D65] flex items-center justify-center text-white shadow-sm">
              <FileText className="w-4 h-4 stroke-[2.5]" />
            </div>
            <span className="font-semibold text-lg tracking-tight text-white">
              DocMind
            </span>
          </Link>
        </div>

        <div className="my-10 lg:my-0 space-y-4 max-w-md">
          <h1 className="text-3xl lg:text-4xl font-bold tracking-tight text-white leading-tight">
            Ask your documents. <br />
            Inspect the supporting pages.
          </h1>
          <p className="text-sm text-[#A5BDB4] leading-relaxed">
            Sign in to work with text-based PDFs, inspect extracted pages locally before AI processing, and trace every claim back to physical PDF page numbers.
          </p>
        </div>

        {/* Authentic Product Scope Summary Card */}
        <div className="p-5 rounded-2xl bg-[#193730] border border-[#274E45] shadow-lg max-w-md space-y-3">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#4ADE80]">
            <Lock className="w-3 h-3" />
            <span>Session-Isolated PDF Q&A</span>
          </div>

          <ul className="space-y-2 text-xs text-[#D1E0DA]">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#4ADE80] shrink-0 mt-0.5" />
              <span>Local PDF page preview with zero AI API calls</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#4ADE80] shrink-0 mt-0.5" />
              <span>Physical page citations verified against retrieved text chunks</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#4ADE80] shrink-0 mt-0.5" />
              <span>Explicit provider consent &amp; account-scoped saved workspaces</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Right Form Container */}
      <div className="flex-1 flex flex-col justify-between p-6 lg:p-12 bg-white dark:bg-[#10221F]">
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            title={`Switch to ${resolvedTheme === "dark" ? "light" : "dark"} mode`}
            className="w-8 h-8 rounded-full border border-[#E5EBE8] dark:border-[#28483F] flex items-center justify-center text-[#5C7069] dark:text-[#9FB1AA] hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831] transition-colors"
          >
            {resolvedTheme === "dark" ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-[#172B28]" />
            )}
          </button>
        </div>

        <div className="w-full max-w-md mx-auto my-auto py-6">{children}</div>

        <div className="text-center text-[11px] text-[#8A9C96] dark:text-[#738C84]">
          Text-based PDFs only · Max 10 files · 10 MB each · 200 pages per session
        </div>
      </div>
    </div>
  );
}
