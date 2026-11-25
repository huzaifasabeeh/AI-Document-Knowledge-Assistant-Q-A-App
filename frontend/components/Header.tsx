"use client";

import React from "react";
import { BookOpen, Laptop, Menu, Moon, Sun } from "lucide-react";
import { useTheme } from "@/lib/theme-context";
import { useAuth } from "@/lib/auth-context";
import { useDocs } from "@/lib/doc-context";

interface HeaderProps {
  onOpenMobileSidebar?: () => void;
}

export function Header({ onOpenMobileSidebar }: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const { health } = useAuth();
  const {
    documents,
    indexed,
    passageCount,
    messages,
    savedWorkspaceId,
    activeSources,
    isEvidenceOpen,
    openEvidence,
    closeEvidence,
  } = useDocs();

  const indexedDocsCount = indexed ? documents.length : 0;
  const responseCount = messages.filter((m) => m.role === "assistant").length;
  const providerLabel = health?.ai?.label || "Unconfigured";

  return (
    <header className="min-h-14 border-b border-[#E5EBE8] dark:border-[#22423B] bg-white dark:bg-[#132723] px-4 lg:px-6 py-2 flex flex-wrap items-center justify-between gap-3 transition-colors duration-200">
      {/* Left title + provider badge */}
      <div className="flex items-center gap-2.5 min-w-0">
        {onOpenMobileSidebar && (
          <button
            type="button"
            onClick={onOpenMobileSidebar}
            aria-label="Open sidebar"
            className="md:hidden p-1.5 rounded-lg border border-[#E5EBE8] dark:border-[#28483F] text-[#172B28] dark:text-[#F2F7F5]"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}
        <h1 className="text-sm font-semibold text-[#172B28] dark:text-[#F2F7F5] truncate">
          Document Knowledge Assistant
        </h1>
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
          {providerLabel}
        </span>
        {savedWorkspaceId && (
          <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#F1F5F3] dark:bg-[#1E3B33] text-[#5C7069] dark:text-[#9FB1AA]">
            Saved workspace open
          </span>
        )}
      </div>

      {/* Right telemetry pills + Appearance + Evidence toggle */}
      <div className="flex items-center gap-2.5 flex-wrap">
        <div className="hidden lg:flex items-center gap-2 text-[11px] text-[#5C7069] dark:text-[#9FB1AA]">
          <span className="px-2.5 py-1 rounded-lg bg-[#F6F8F7] dark:bg-[#172E29] border border-[#E5EBE8] dark:border-[#25463D]">
            Indexed docs: <strong className="text-[#172B28] dark:text-[#F2F7F5]">{indexedDocsCount}</strong>
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-[#F6F8F7] dark:bg-[#172E29] border border-[#E5EBE8] dark:border-[#25463D]">
            Passages: <strong className="text-[#172B28] dark:text-[#F2F7F5]">{passageCount}</strong>
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-[#F6F8F7] dark:bg-[#172E29] border border-[#E5EBE8] dark:border-[#25463D]">
            Responses: <strong className="text-[#172B28] dark:text-[#F2F7F5]">{responseCount}</strong>
          </span>
        </div>

        {/* Light / Dark / System Segmented Switcher */}
        <div
          role="group"
          aria-label="Appearance theme"
          className="inline-flex items-center p-0.5 rounded-full border border-[#E5EBE8] dark:border-[#28483F] bg-[#F6F8F7] dark:bg-[#10221F]"
        >
          <button
            type="button"
            onClick={() => setTheme("light")}
            title="Light theme"
            aria-label="Light theme"
            className={`p-1.5 rounded-full transition-colors ${
              theme === "light"
                ? "bg-white dark:bg-[#1A3831] text-[#147D65] shadow-xs"
                : "text-[#6B7C77] dark:text-[#94A7A1]"
            }`}
          >
            <Sun className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => setTheme("dark")}
            title="Dark theme"
            aria-label="Dark theme"
            className={`p-1.5 rounded-full transition-colors ${
              theme === "dark"
                ? "bg-white dark:bg-[#1A3831] text-[#4ADE80] shadow-xs"
                : "text-[#6B7C77] dark:text-[#94A7A1]"
            }`}
          >
            <Moon className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => setTheme("system")}
            title="System theme"
            aria-label="System theme"
            className={`p-1.5 rounded-full transition-colors ${
              theme === "system"
                ? "bg-white dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80] shadow-xs"
                : "text-[#6B7C77] dark:text-[#94A7A1]"
            }`}
          >
            <Laptop className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Source Inspector Toggle */}
        {activeSources.length > 0 && (
          <button
            type="button"
            onClick={() => {
              if (isEvidenceOpen) closeEvidence();
              else openEvidence(activeSources, 0);
            }}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              isEvidenceOpen
                ? "bg-[#EAF4EF] dark:bg-[#1A3831] border-[#C8E2D5] dark:border-[#274F44] text-[#147D65] dark:text-[#4ADE80]"
                : "bg-white dark:bg-[#172E29] border-[#E5EBE8] dark:border-[#26483F] text-[#172B28] dark:text-[#F2F7F5]"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Sources ({activeSources.length})</span>
          </button>
        )}
      </div>
    </header>
  );
}
