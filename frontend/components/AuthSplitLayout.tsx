"use client";

import React from "react";
import Link from "next/link";
import { FileText } from "lucide-react";

interface AuthSplitLayoutProps {
  children: React.ReactNode;
}

export function AuthSplitLayout({ children }: AuthSplitLayoutProps) {
  return (
    <div className="min-h-screen w-screen flex flex-col lg:flex-row bg-white dark:bg-[#132723]">
      {/* Left Hero Panel (Dark Forest Teal) */}
      <div className="lg:w-5/12 bg-[#122A24] dark:bg-[#0E201B] p-8 lg:p-14 text-white flex flex-col justify-between relative overflow-hidden select-none">
        {/* Top Logo */}
        <div>
          <Link href="/" className="inline-flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#147D65] flex items-center justify-center text-white shadow-sm">
              <FileText className="w-4 h-4 stroke-[2.5]" />
            </div>
            <span className="font-semibold text-lg tracking-tight text-white">
              DocuMind
            </span>
          </Link>
        </div>

        {/* Center Hero Text */}
        <div className="my-12 lg:my-0 space-y-4 max-w-md">
          <h1 className="text-3xl lg:text-5xl font-bold tracking-tight text-white leading-tight">
            Your documents. <br />
            A little more intelligent.
          </h1>
          <p className="text-sm lg:text-base text-[#9BB3AA] leading-relaxed">
            Turn scattered information into clear answers. Grounded in your knowledge. Backed by sources.
          </p>
        </div>

        {/* Bottom Grounding Quote Card */}
        <div className="p-5 rounded-2xl bg-[#193730] border border-[#274E45] shadow-lg max-w-md space-y-3">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#4ADE80]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#4ADE80]" />
            <span>Grounded in your documents</span>
          </div>

          <h3 className="text-sm font-bold text-white">
            Clarity, with a citation.
          </h3>

          <p className="text-xs text-[#D1E0DA] leading-relaxed italic">
            &ldquo;Revenue grew 24% in Q3, led by enterprise expansion and stronger retention.&rdquo;
          </p>

          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#142B25] text-[#9FB6AD] border border-[#23473E]">
            <FileText className="w-3 h-3 text-[#4ADE80]" />
            <span>Q3 Financial Report • Page 8</span>
          </div>
        </div>
      </div>

      {/* Right Form Container */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-white dark:bg-[#10221F]">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
