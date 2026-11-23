"use client";

import React from "react";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { ChatArea } from "@/components/ChatArea";
import { SourceEvidencePanel } from "@/components/SourceEvidencePanel";

export default function WorkspacePage() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F6F8F7] dark:bg-[#10221F]">
      {/* Column 1: Left Navigation Sidebar */}
      <Sidebar />

      {/* Column 2: Center Main Content & Header */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header
          title="Q3 performance overview"
          badge="AI knowledge assistant"
        />
        <ChatArea />
      </div>

      {/* Column 3: Right Source Evidence Panel */}
      <SourceEvidencePanel />
    </div>
  );
}
