"use client";

import React from "react";
import { CheckCircle2, FileText, X } from "lucide-react";
import { useDocs } from "@/lib/doc-context";

export function SourceEvidencePanel() {
  const { activeSources, activeSourceIndex, isEvidenceOpen, openEvidence, closeEvidence } =
    useDocs();

  if (!isEvidenceOpen || activeSources.length === 0) {
    return null;
  }

  return (
    <aside className="w-80 lg:w-96 flex-shrink-0 border-l border-[#E5EBE8] dark:border-[#22423B] bg-white dark:bg-[#132723] flex flex-col h-full overflow-hidden transition-colors duration-200">
      {/* Header */}
      <div className="p-4 border-b border-[#E5EBE8] dark:border-[#22423B]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold text-[#172B28] dark:text-[#F2F7F5]">
              Supporting passages
            </h2>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
              {activeSources.length}
            </span>
          </div>
          <button
            type="button"
            onClick={closeEvidence}
            aria-label="Close supporting passages"
            className="w-7 h-7 rounded-md hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831] flex items-center justify-center text-[#6B7C77] dark:text-[#94A7A1]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
          Compare each cited claim against the extracted PDF text.
        </p>
      </div>

      {/* Passages List */}
      <div className="p-4 space-y-3 overflow-y-auto flex-1">
        {activeSources.map((source, idx) => {
          const isSelected = idx === activeSourceIndex;
          return (
            <div
              key={`${source.filename}-${source.page}-${idx}`}
              onClick={() => openEvidence(activeSources, idx)}
              className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-2 ${
                isSelected
                  ? "border-[#147D65] dark:border-[#4ADE80] bg-[#EAF4EF]/60 dark:bg-[#1A3831]/80"
                  : "border-[#E5EBE8] dark:border-[#25463D] bg-[#FAFCFB] dark:bg-[#152B26] hover:border-[#147D65]/40"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80] shrink-0" />
                  <span className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5] truncate">
                    {source.filename}
                  </span>
                </div>
                <span className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-white dark:bg-[#10221F] border border-[#E5EBE8] dark:border-[#274F44] text-[#147D65] dark:text-[#4ADE80] shrink-0">
                  PDF page {source.page}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-white dark:bg-[#10221F] border border-[#E5EBE8] dark:border-[#25463D]">
                <p className="text-xs text-[#172B28] dark:text-[#E2EBE7] whitespace-pre-wrap leading-relaxed">
                  {source.text}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer note */}
      <div className="p-3 border-t border-[#E5EBE8] dark:border-[#22423B] flex items-center gap-2 text-[11px] text-[#5C7069] dark:text-[#9FB1AA] bg-[#FAFCFB] dark:bg-[#112420]">
        <CheckCircle2 className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80] shrink-0" />
        <span>Citations do not guarantee accuracy; verify against your PDF.</span>
      </div>
    </aside>
  );
}
