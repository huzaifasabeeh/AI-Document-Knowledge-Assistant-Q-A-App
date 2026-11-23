"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { AuthGuard } from "@/components/AuthGuard";
import {
  FileText,
  UploadCloud,
  Search,
  Filter,
  MoreVertical,
  Plus,
  CheckCircle2,
  Folder,
  Trash2,
} from "lucide-react";
import { useDocs } from "@/lib/doc-context";
import { DocumentStatus } from "@/lib/types";

export default function DocumentsPage() {
  const { documents, collections, uploadRealFiles, isUploading, storageUsedMb } = useDocs();
  const [showUploadZone, setShowUploadZone] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCollection, setSelectedCollection] = useState("All collections");
  const [targetCollection, setTargetCollection] = useState(collections[0]?.name || "General");
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCol =
      selectedCollection === "All collections" || doc.collection === selectedCollection;
    return matchesSearch && matchesCol;
  });

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    uploadRealFiles(Array.from(files), targetCollection);
    setShowUploadZone(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const renderStatusBadge = (status: DocumentStatus, progress?: number) => {
    switch (status) {
      case "ready":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
            Ready
          </span>
        );
      case "indexing":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#FEF3C7] dark:bg-[#3D2C12] text-[#B45309] dark:text-[#FBBF24]">
            Indexing - {progress || 68}%
          </span>
        );
      case "attention":
      case "failed":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#FEE2E2] dark:bg-[#3D1A1A] text-[#DC2626] dark:text-[#F87171]">
            Upload failed
          </span>
        );
    }
  };

  const readyCount = documents.filter((d) => d.status === "ready").length;
  const indexingCount = documents.filter((d) => d.status === "indexing").length;
  const attentionCount = documents.filter((d) => d.status === "attention" || d.status === "failed").length;

  return (
    <AuthGuard>
      <div className="flex h-screen w-screen overflow-hidden bg-[#F6F8F7] dark:bg-[#10221F]">
        <Sidebar />

        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <Header title="Documents" badge="AI knowledge assistant" />

          <div className="flex-1 overflow-y-auto p-6 lg:p-10 space-y-6">
            {/* Header row */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
                  Your documents
                </h1>
                <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
                  Your source of truth, organized and ready to explore.
                </p>
              </div>
              <button
                onClick={() => setShowUploadZone(!showUploadZone)}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] text-white font-medium text-xs shadow-xs transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>{showUploadZone ? "Hide upload area" : "+ Upload documents"}</span>
              </button>
            </div>

            {/* 4 Stats Cards (Dynamic Real-time) */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs">
                <div className="text-2xl font-bold text-[#172B28] dark:text-[#F2F7F5]">
                  {documents.length}
                </div>
                <div className="text-xs font-semibold text-[#172B28] dark:text-[#E2EBE7] mt-1">
                  Total documents
                </div>
                <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
                  {storageUsedMb.toFixed(1)} MB used
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs">
                <div className="text-2xl font-bold text-[#147D65] dark:text-[#4ADE80]">
                  {readyCount}
                </div>
                <div className="text-xs font-semibold text-[#172B28] dark:text-[#E2EBE7] mt-1">
                  Ready for questions
                </div>
                <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
                  Indexed and searchable
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs">
                <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                  {indexingCount}
                </div>
                <div className="text-xs font-semibold text-[#172B28] dark:text-[#E2EBE7] mt-1">
                  Currently indexing
                </div>
                <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
                  Available shortly
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs">
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {attentionCount}
                </div>
                <div className="text-xs font-semibold text-[#172B28] dark:text-[#E2EBE7] mt-1">
                  Needs attention
                </div>
                <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
                  Upload a new copy
                </div>
              </div>
            </div>

            {/* Upload Dropzone Section */}
            {showUploadZone && (
              <div className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all">
                <div className="lg:col-span-2">
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-[#147D65]/40 dark:border-[#4ADE80]/30 hover:border-[#147D65] bg-[#FAFCFB] dark:bg-[#122420] rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors"
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={(e) => handleFiles(e.target.files)}
                      multiple
                      accept=".pdf,.docx,.txt"
                      className="hidden"
                    />
                    <div className="w-12 h-12 rounded-xl bg-[#EAF4EF] dark:bg-[#1B3831] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80] mb-3">
                      <UploadCloud className="w-6 h-6" />
                    </div>
                    <h3 className="text-base font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                      {isUploading ? "Uploading & Indexing into Chroma..." : "Drop your documents here"}
                    </h3>
                    <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
                      or choose files from your computer
                    </p>
                    <button
                      type="button"
                      className="mt-4 px-4 py-2 rounded-xl bg-[#147D65] text-white text-xs font-medium"
                    >
                      Browse files
                    </button>
                    <span className="text-[11px] text-[#8A9C96] dark:text-[#718B82] mt-3">
                      PDF, DOCX or TXT • Up to 25 MB per file
                    </span>
                  </div>
                </div>

                {/* Upload options sidebar */}
                <div className="space-y-4">
                  <div className="p-4 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-[#FAFCFB] dark:bg-[#142925] space-y-3">
                    <div className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                      Add to collection
                    </div>
                    <p className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                      Keep related sources together for more focused answers.
                    </p>
                    <select
                      value={targetCollection}
                      onChange={(e) => setTargetCollection(e.target.value)}
                      className="w-full text-xs p-2 rounded-lg border border-[#E5EBE8] dark:border-[#28483F] bg-white dark:bg-[#1A352F] text-[#172B28] dark:text-[#F2F7F5]"
                    >
                      {collections.map((col) => (
                        <option key={col.id} value={col.name}>
                          {col.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="p-4 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-[#FAFCFB] dark:bg-[#142925] space-y-2 text-xs">
                    <div className="font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                      From document to knowledge
                    </div>
                    <div className="flex items-start gap-2 text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80] shrink-0 mt-0.5" />
                      <span>Upload securely (Encrypted at rest)</span>
                    </div>
                    <div className="flex items-start gap-2 text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80] shrink-0 mt-0.5" />
                      <span>Extract & index meaningful passages</span>
                    </div>
                    <div className="flex items-start gap-2 text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-[#147D65] dark:text-[#4ADE80] shrink-0 mt-0.5" />
                      <span>Ask with confidence backed by citations</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Search and Filters Bar */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="relative w-full sm:w-80">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-[#8A9C96]" />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-white dark:bg-[#162E29] text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
                />
              </div>

              <div className="flex items-center gap-2 w-full sm:w-auto">
                <select
                  value={selectedCollection}
                  onChange={(e) => setSelectedCollection(e.target.value)}
                  className="text-xs px-3 py-2 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-white dark:bg-[#162E29] text-[#172B28] dark:text-[#F2F7F5]"
                >
                  <option value="All collections">All collections</option>
                  {collections.map((col) => (
                    <option key={col.id} value={col.name}>
                      {col.name}
                    </option>
                  ))}
                </select>

                <button className="text-xs px-3 py-2 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-white dark:bg-[#162E29] text-[#172B28] dark:text-[#F2F7F5] flex items-center gap-1.5">
                  <Filter className="w-3.5 h-3.5" />
                  <span>Status ▾</span>
                </button>
              </div>
            </div>

            {/* Documents Table */}
            <div className="rounded-2xl border border-[#E5EBE8] dark:border-[#26483F] bg-white dark:bg-[#162E29] overflow-hidden shadow-xs">
              {filteredDocs.length === 0 ? (
                <div className="p-12 text-center space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-[#EAF4EF] dark:bg-[#1A3831] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80] mx-auto">
                    <FileText className="w-6 h-6" />
                  </div>
                  <h3 className="text-sm font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                    No documents uploaded yet
                  </h3>
                  <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] max-w-sm mx-auto">
                    Drag and drop your PDF or DOCX files above to index them into your private knowledge base.
                  </p>
                  <button
                    onClick={() => setShowUploadZone(true)}
                    className="px-4 py-2 rounded-xl bg-[#147D65] text-white text-xs font-medium hover:bg-[#0E634F] transition-colors"
                  >
                    + Upload your first document
                  </button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-[#E5EBE8] dark:border-[#22423B] bg-[#FAFCFB] dark:bg-[#132824] text-[11px] font-semibold text-[#6B7C77] dark:text-[#94A7A1]">
                        <th className="p-3.5 pl-4 w-10">
                          <input type="checkbox" className="rounded text-[#147D65]" />
                        </th>
                        <th className="p-3.5">Name</th>
                        <th className="p-3.5">Collection</th>
                        <th className="p-3.5">Size</th>
                        <th className="p-3.5">Status</th>
                        <th className="p-3.5">Added</th>
                        <th className="p-3.5 text-right pr-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E5EBE8] dark:divide-[#22423B] text-xs">
                      {filteredDocs.map((doc) => (
                        <tr
                          key={doc.id}
                          className="hover:bg-[#F6F8F7] dark:hover:bg-[#18332D] transition-colors"
                        >
                          <td className="p-3.5 pl-4">
                            <input type="checkbox" className="rounded text-[#147D65]" />
                          </td>
                          <td className="p-3.5">
                            <div className="flex items-center gap-2.5">
                              <div className="w-7 h-7 rounded-lg bg-[#EAF4EF] dark:bg-[#1A3831] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80] shrink-0">
                                <FileText className="w-3.5 h-3.5" />
                              </div>
                              <div>
                                <div className="font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                                  {doc.name}
                                </div>
                                <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                                  {doc.type.toUpperCase()} • {doc.pages} {doc.pages === 1 ? "page" : "pages"}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="p-3.5 text-[#4A5D57] dark:text-[#AFC1B9]">
                            {doc.collection}
                          </td>
                          <td className="p-3.5 text-[#6B7C77] dark:text-[#94A7A1]">{doc.size}</td>
                          <td className="p-3.5">{renderStatusBadge(doc.status, doc.indexingProgress)}</td>
                          <td className="p-3.5 text-[#6B7C77] dark:text-[#94A7A1]">{doc.addedAt}</td>
                          <td className="p-3.5 text-right pr-4">
                            <button className="p-1 rounded-md hover:bg-[#E5EBE8] dark:hover:bg-[#203D35] text-[#6B7C77]">
                              <MoreVertical className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Pagination footer */}
              {filteredDocs.length > 0 && (
                <div className="p-4 border-t border-[#E5EBE8] dark:border-[#22423B] flex items-center justify-between text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                  <div>Showing {filteredDocs.length} of {documents.length} documents</div>
                  <div className="flex items-center gap-1.5">
                    <button className="px-2.5 py-1 rounded-lg border border-[#E5EBE8] dark:border-[#25463D] hover:bg-[#F6F8F7] dark:hover:bg-[#1E3B33]">
                      Previous
                    </button>
                    <button className="w-7 h-7 rounded-lg bg-[#147D65] text-white font-medium">
                      1
                    </button>
                    <button className="px-2.5 py-1 rounded-lg border border-[#E5EBE8] dark:border-[#25463D] hover:bg-[#F6F8F7] dark:hover:bg-[#1E3B33]">
                      Next
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
