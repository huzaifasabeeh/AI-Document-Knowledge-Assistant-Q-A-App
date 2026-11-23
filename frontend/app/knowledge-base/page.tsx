"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { AuthGuard } from "@/components/AuthGuard";
import {
  Folder,
  Plus,
  ArrowUpRight,
  Sparkles,
  Search,
  MoreVertical,
  CheckCircle2,
  FileText,
} from "lucide-react";
import { useDocs } from "@/lib/doc-context";
import { useRouter } from "next/navigation";

export default function KnowledgeBasePage() {
  const { collections, documents, createCollection, startNewChat, uploadQueue } = useDocs();
  const router = useRouter();
  const [filterTab, setFilterTab] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [newColName, setNewColName] = useState("");
  const [newColDesc, setNewColDesc] = useState("");

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newColName.trim()) return;
    createCollection(newColName, newColDesc);
    setNewColName("");
    setNewColDesc("");
    setShowModal(false);
  };

  const handleAskCollection = (colName: string) => {
    startNewChat();
    router.push("/");
  };

  const filteredCols = collections.filter((c) =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AuthGuard>
      <div className="flex h-screen w-screen overflow-hidden bg-[#F6F8F7] dark:bg-[#10221F]">
        <Sidebar />

        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <Header title="Knowledge base" badge="AI knowledge assistant" />

          <div className="flex-1 overflow-y-auto p-6 lg:p-10 space-y-6">
            {/* Header row */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
                  Your knowledge base
                </h1>
                <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
                  A home for the knowledge that moves your work forward.
                </p>
              </div>
              <button
                onClick={() => setShowModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] text-white font-medium text-xs shadow-xs transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>+ New collection</span>
              </button>
            </div>

            {/* Operational banner card */}
            <div className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-[#EAF4EF] dark:bg-[#1C3B33] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80]">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#172B28] dark:text-[#F2F7F5]">
                    Knowledge, connected.
                  </h3>
                  <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
                    {documents.length} {documents.length === 1 ? "document" : "documents"} indexed across {collections.length} collections. Your answers are grounded in your sources.
                  </p>
                </div>
              </div>

              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]">
                <span className="w-2 h-2 rounded-full bg-[#147D65] dark:bg-[#4ADE80]" />
                <span>All systems operational</span>
              </div>
            </div>

            {/* Tabs and search row */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setFilterTab("all")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    filterTab === "all"
                      ? "bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]"
                      : "text-[#6B7C77] dark:text-[#94A7A1] hover:text-[#172B28]"
                  }`}
                >
                  All collections
                </button>
              </div>

              <div className="relative w-full sm:w-64">
                <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-[#8A9C96]" />
                <input
                  type="text"
                  placeholder="Search collections..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-white dark:bg-[#162E29] text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden"
                />
              </div>
            </div>

            {/* Collections Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredCols.map((col) => {
                const colDocs = documents.filter((d) => d.collection === col.name);
                return (
                  <div
                    key={col.id}
                    className="p-5 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs flex flex-col justify-between hover:border-[#147D65] dark:hover:border-[#4ADE80] transition-all group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-9 h-9 rounded-xl bg-[#EAF4EF] dark:bg-[#1E3B33] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80]">
                          <Folder className="w-4 h-4" />
                        </div>
                        <button className="text-[#8A9C96] hover:text-[#172B28]">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>

                      <h3 className="text-base font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                        {col.name}
                      </h3>
                      <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1.5 leading-relaxed">
                        {col.description}
                      </p>
                    </div>

                    <div className="pt-6 mt-4 border-t border-[#E5EBE8] dark:border-[#25463D] space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-[#172B28] dark:text-[#E2EBE7]">
                          {colDocs.length} {colDocs.length === 1 ? "document" : "documents"}
                        </span>
                        <span className="text-[11px] text-[#8A9C96] dark:text-[#738C84]">Private</span>
                      </div>

                      <div className="text-[11px] font-medium text-[#147D65] dark:text-[#4ADE80]">
                        {colDocs.filter((d) => d.status === "ready").length} indexed
                      </div>

                      <button
                        onClick={() => handleAskCollection(col.name)}
                        className="w-full flex items-center justify-between pt-1 text-xs font-semibold text-[#147D65] dark:text-[#4ADE80] group-hover:underline"
                      >
                        <span>Ask this collection</span>
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Indexing Activity section */}
            <div className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-[#172B28] dark:text-[#F2F7F5]">
                  Indexing activity
                </h2>
                <span className="text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                  Chroma Vector Store
                </span>
              </div>

              {uploadQueue.length > 0 ? (
                <div className="space-y-3">
                  {uploadQueue.slice(0, 3).map((item, idx) => (
                    <div
                      key={idx}
                      className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-[#FAFCFB] dark:bg-[#142925]"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="w-4 h-4 text-[#147D65] dark:text-[#4ADE80]" />
                        <div>
                          <div className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                            {item.name}
                          </div>
                          <div className="text-[11px] text-[#6B7C77] dark:text-[#94A7A1]">
                            {item.status} • {item.size}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 w-full sm:w-60">
                        <div className="flex-1 bg-[#E5EBE8] dark:bg-[#25423A] h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-[#147D65] h-full rounded-full transition-all duration-300"
                            style={{ width: `${item.progress}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                          {item.progress}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                  All indexed document embeddings are up-to-date and ready for queries.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* New Collection Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
            <form
              onSubmit={handleCreate}
              className="w-full max-w-md bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] rounded-2xl p-6 shadow-xl space-y-4"
            >
              <h3 className="text-lg font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                Create new collection
              </h3>

              <div>
                <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                  Collection name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Finance, Legal, Research"
                  value={newColName}
                  onChange={(e) => setNewColName(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-sm text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                  Description
                </label>
                <textarea
                  rows={3}
                  placeholder="Briefly describe what documents belong here..."
                  value={newColDesc}
                  onChange={(e) => setNewColDesc(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-sm text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-medium text-[#6B7C77] hover:bg-[#F6F8F7] dark:hover:bg-[#1A352F]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl text-xs font-medium bg-[#147D65] hover:bg-[#0E634F] text-white"
                >
                  Create collection
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </AuthGuard>
  );
}
