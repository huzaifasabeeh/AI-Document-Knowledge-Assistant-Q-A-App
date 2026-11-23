"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  FileText,
  Search,
  BookOpen,
  Clock,
  Settings,
  Plus,
  ChevronDown,
  ExternalLink,
  MessageSquare,
} from "lucide-react";
import { useDocs } from "@/lib/doc-context";
import { useAuth } from "@/lib/auth-context";

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { startNewChat } = useDocs();
  const { user } = useAuth();

  const handleNewChat = () => {
    startNewChat();
    router.push("/");
  };

  const navItems = [
    { label: "Search", href: "/search", icon: Search },
    { label: "Documents", href: "/documents", icon: FileText },
    { label: "Knowledge base", href: "/knowledge-base", icon: BookOpen },
    { label: "Chat history", href: "/history", icon: Clock },
  ];

  const recentChats = [
    { title: "Q3 performance overview", active: pathname === "/" },
    { title: "Compare vendor proposals", active: false },
    { title: "Onboarding policy summary", active: false },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-[#E5EBE8] dark:border-[#22423B] bg-white dark:bg-[#132723] flex flex-col justify-between h-screen overflow-y-auto select-none transition-colors duration-200">
      <div>
        {/* App Brand Header */}
        <div className="p-4 flex items-center justify-between border-b border-[#E5EBE8] dark:border-[#22423B]">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#147D65] flex items-center justify-center text-white shadow-sm">
              <FileText className="w-4 h-4 stroke-[2.5]" />
            </div>
            <span className="font-semibold text-lg tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
              DocuMind
            </span>
          </Link>
          <div className="w-5 h-5 rounded border border-[#E5EBE8] dark:border-[#2A4B42] flex items-center justify-center text-[#6B7C77] dark:text-[#94A7A1] text-xs">
            ⌘
          </div>
        </div>

        {/* Workspace selector */}
        <div className="px-4 pt-3 pb-2">
          <button className="flex items-center gap-1.5 text-xs text-[#6B7C77] dark:text-[#94A7A1] hover:text-[#172B28] dark:hover:text-white font-medium transition-colors">
            <span>{user?.workspaceName || "Personal workspace"}</span>
            <ChevronDown className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* New chat action */}
        <div className="px-3 py-2">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80] font-medium text-sm hover:bg-[#D8EBE1] dark:hover:bg-[#23473E] transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New chat</span>
          </button>
        </div>

        {/* Main Navigation */}
        <nav className="px-3 py-2 space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.label}
                href={item.href}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]"
                    : "text-[#4A5D57] dark:text-[#9FB1AA] hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831]/50 hover:text-[#172B28] dark:hover:text-white"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Recent Chats */}
        <div className="px-4 pt-6 pb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[#8A9C96] dark:text-[#738C84]">
            Recent chats
          </span>
          <div className="mt-2 space-y-1">
            {recentChats.map((chat) => (
              <Link
                key={chat.title}
                href="/"
                className={`flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs transition-colors ${
                  chat.active
                    ? "bg-[#F1F6F4] dark:bg-[#1D3B34] text-[#172B28] dark:text-white font-medium"
                    : "text-[#5C7069] dark:text-[#9FB1AA] hover:bg-[#F6F8F7] dark:hover:bg-[#18332D]"
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5 text-[#8A9C96]" />
                <span className="truncate">{chat.title}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Footer / Storage & Settings */}
      <div className="p-3 border-t border-[#E5EBE8] dark:border-[#22423B] space-y-3">
        {/* Storage card */}
        <div className="p-3 rounded-lg bg-[#F6F8F7] dark:bg-[#172E29] border border-[#E5EBE8] dark:border-[#26443B]">
          <div className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
            Your knowledge, connected
          </div>
          <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] mt-1">
            {user?.storageUsedMb || 128} MB of {((user?.storageLimitMb || 1024) / 1024).toFixed(0)} GB used
          </div>
          <div className="w-full bg-[#E5EBE8] dark:bg-[#25423A] h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className="bg-[#147D65] h-full rounded-full"
              style={{
                width: `${((user?.storageUsedMb || 128) / (user?.storageLimitMb || 1024)) * 100}%`,
              }}
            />
          </div>
          <Link
            href="/settings"
            className="mt-2.5 flex items-center gap-1 text-[11px] font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
          >
            <span>Upgrade to Pro</span>
            <ExternalLink className="w-3 h-3" />
          </Link>
        </div>

        {/* Settings Button */}
        <Link
          href="/settings"
          className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            pathname === "/settings"
              ? "bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]"
              : "text-[#4A5D57] dark:text-[#9FB1AA] hover:bg-[#F6F8F7] dark:hover:bg-[#18332D]"
          }`}
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </Link>
      </div>
    </aside>
  );
}
