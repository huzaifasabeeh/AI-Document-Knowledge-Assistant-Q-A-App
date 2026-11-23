"use client";

import React, { useState } from "react";
import {
  X,
  FileText,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  CheckCircle2,
} from "lucide-react";
import { useDocs } from "@/lib/doc-context";

export function SourceEvidencePanel() {
  const { activeEvidence, isEvidenceOpen, closeEvidence } = useDocs();
  const [currentPage, setCurrentPage] = useState(activeEvidence?.page || 1);

  if (!isEvidenceOpen || !activeEvidence) {
    return null;
  }

  const prevPage = () => {
    if (currentPage > 1) setCurrentPage((p) => p - 1);
  };

  const nextPage = () => {
    if (currentPage < activeEvidence.totalPages) setCurrentPage((p) => p + 1);
  };

  return (
    <aside className="w-80 lg:w-96 flex-shrink-0 border-l border-[#E5EBE8] dark:border-[#22423B] bg-white dark:bg-[#132723] flex flex-col h-screen overflow-y-auto select-none transition-colors duration-200">
      {/* Top Header */}
      <div className="p-4 border-b border-[#E5EBE8] dark:border-[#22423B]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold text-[#172B28] dark:text-[#F2F7F5]">
              Source evidence
            </h2>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
              Grounded
            </span>
          </div>
          <button
            onClick={closeEvidence}
            className="w-7 h-7 rounded-md hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831] flex items-center justify-center text-[#6B7C77] dark:text-[#94A7A1] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
          Every claim links directly to its source.
        </p>
      </div>

      <div className="p-4 space-y-4 flex-1">
        {/* Document metadata card */}
        <div className="p-3.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-[#FAFCFB] dark:bg-[#172E29]">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-[#EAF4EF] dark:bg-[#1A3831] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80]">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                  {activeEvidence.docTitle}
                </div>
                <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                  {activeEvidence.docType}
                </div>
              </div>
            </div>
          </div>

          {/* Page navigator */}
          <div className="mt-3 pt-3 border-t border-[#E5EBE8] dark:border-[#25463D] flex items-center justify-between text-xs text-[#5C7069] dark:text-[#9FB1AA]">
            <span>
              Page {activeEvidence.page} of {activeEvidence.totalPages}
            </span>
          </div>
        </div>

        {/* Paper Page Simulation */}
        <div className="p-4 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-white dark:bg-[#152B26] shadow-xs space-y-3 font-serif">
          <div className="text-[10px] tracking-widest uppercase font-semibold text-[#8A9C96] dark:text-[#718B82] font-sans">
            {activeEvidence.docTitle}
          </div>
          <h3 className="text-xs font-bold text-[#172B28] dark:text-[#F2F7F5] font-sans">
            {activeEvidence.heading}
          </h3>

          {/* Highlighted Evidence snippet */}
          <div className="p-3 rounded-lg bg-[#EAF4EF] dark:bg-[#1C3E36] border-l-3 border-[#147D65] dark:border-[#4ADE80]">
            <p className="text-xs leading-relaxed text-[#172B28] dark:text-[#E2EBE7] font-medium font-sans">
              {activeEvidence.highlightSnippet || activeEvidence.fullText}
            </p>
          </div>

          {activeEvidence.fullText && activeEvidence.fullText !== activeEvidence.highlightSnippet && (
            <p className="text-xs leading-relaxed text-[#4A5D57] dark:text-[#AFC1B9] whitespace-pre-line">
              {activeEvidence.fullText}
            </p>
          )}
        </div>

        {/* Related Passages */}
        {activeEvidence.relatedPassages && activeEvidence.relatedPassages.length > 0 && (
          <div className="pt-2">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-[#8A9C96] dark:text-[#738C84] mb-2.5">
              Related passages
            </div>
            <div className="space-y-2">
              {activeEvidence.relatedPassages.map((passage) => (
                <div
                  key={passage.num}
                  className="p-2.5 rounded-lg border border-[#E5EBE8] dark:border-[#25463D] hover:bg-[#FAFCFB] dark:hover:bg-[#1A352F] cursor-pointer transition-colors flex items-start gap-2.5"
                >
                  <div className="w-5 h-5 rounded-md bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80] font-semibold text-[11px] flex items-center justify-center shrink-0">
                    {passage.num}
                  </div>
                  <div>
                    <div className="text-xs font-medium text-[#172B28] dark:text-[#F2F7F5]">
                      {passage.title}
                    </div>
                    <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                      {passage.docAndPage}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer grounded confirmation */}
      <div className="p-3 border-t border-[#E5EBE8] dark:border-[#22423B] flex items-center gap-2 text-[11px] text-[#147D65] dark:text-[#4ADE80] bg-[#FAFCFB] dark:bg-[#142925]">
        <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
        <span>Grounded in indexed vector embeddings.</span>
      </div>
    </aside>
  );
}
