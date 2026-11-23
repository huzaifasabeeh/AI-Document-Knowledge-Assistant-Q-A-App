"use client";

import React from "react";
import Link from "next/link";
import { Lock, Sun, Moon, Sparkles } from "lucide-react";
import { useTheme } from "@/lib/theme-context";
import { useAuth } from "@/lib/auth-context";

interface HeaderProps {
  title?: string;
  badge?: string;
  secondaryBadge?: string;
}

export function Header({
  title = "Workspace",
  badge = "AI knowledge assistant",
  secondaryBadge,
}: HeaderProps) {
  const { resolvedTheme, setTheme } = useTheme();
  const { user } = useAuth();

  const toggleTheme = () => {
    setTheme(resolvedTheme === "dark" ? "light" : "dark");
  };

  return (
    <header className="h-14 border-b border-[#E5EBE8] dark:border-[#22423B] bg-white dark:bg-[#132723] px-6 flex items-center justify-between transition-colors duration-200">
      {/* Left breadcrumb info */}
      <div className="flex items-center gap-2.5">
        <span className="text-sm font-semibold text-[#172B28] dark:text-[#F2F7F5]">
          {title}
        </span>
        {badge && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
            <Sparkles className="w-2.5 h-2.5" />
            {badge}
          </span>
        )}
        {secondaryBadge && (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#F1F5F3] dark:bg-[#1E3B33] text-[#5C7069] dark:text-[#9FB1AA]">
            {secondaryBadge}
          </span>
        )}
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3">
        {/* Private workspace badge */}
        <div className="flex items-center gap-1.5 text-xs text-[#6B7C77] dark:text-[#94A7A1] border border-[#E5EBE8] dark:border-[#28483F] px-2.5 py-1 rounded-full">
          <Lock className="w-3 h-3 text-[#147D65] dark:text-[#4ADE80]" />
          <span>Private workspace</span>
        </div>

        {/* Theme switcher button */}
        <button
          onClick={toggleTheme}
          title={`Switch to ${resolvedTheme === "dark" ? "light" : "dark"} mode`}
          className="w-8 h-8 rounded-full border border-[#E5EBE8] dark:border-[#28483F] flex items-center justify-center text-[#5C7069] dark:text-[#9FB1AA] hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831] transition-colors"
        >
          {resolvedTheme === "dark" ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-[#172B28]" />
          )}
        </button>

        {/* Profile Avatar */}
        <Link href="/settings" className="relative block">
          {user?.avatarUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={user.avatarUrl}
              alt={user.name}
              className="w-8 h-8 rounded-full object-cover ring-2 ring-[#147D65]/20 hover:ring-[#147D65] transition-all"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-[#147D65] text-white flex items-center justify-center font-medium text-xs">
              {user?.name?.slice(0, 2).toUpperCase() || "AM"}
            </div>
          )}
        </Link>
      </div>
    </header>
  );
}
