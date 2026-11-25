"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { ChatArea } from "@/components/ChatArea";
import { SourceEvidencePanel } from "@/components/SourceEvidencePanel";
import { AuthGuard } from "@/components/AuthGuard";

export default function WorkspacePage() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <AuthGuard>
      <div className="flex h-screen w-screen overflow-hidden bg-[#F6F8F7] dark:bg-[#10221F]">
        {/* Column 1: Session Files, Preview, Consent, Indexing & Saved Workspaces */}
        <Sidebar
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() => setMobileSidebarOpen(false)}
        />

        {/* Column 2: Center Header, Metrics, Local Preview & Grounded Q&A */}
        <div className="flex-1 flex flex-col h-screen overflow-hidden min-w-0">
          <Header onOpenMobileSidebar={() => setMobileSidebarOpen(true)} />
          <ChatArea />
        </div>

        {/* Column 3: Supporting Passages Inspector */}
        <SourceEvidencePanel />
      </div>
    </AuthGuard>
  );
}
