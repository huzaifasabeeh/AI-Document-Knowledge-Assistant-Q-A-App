"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import {
  User,
  Shield,
  Palette,
  Check,
  Sun,
  Moon,
  Laptop,
  CheckCircle2,
  AlertTriangle,
  Upload,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useTheme } from "@/lib/theme-context";

export default function SettingsPage() {
  const { user, updateProfile, logout } = useAuth();
  const { theme, setTheme } = useTheme();

  const [activeTab, setActiveTab] = useState<"profile" | "security" | "preferences">("profile");

  // Profile state
  const [name, setName] = useState(user?.name || "Alex Morgan");
  const [email, setEmail] = useState(user?.email || "alex.morgan@acme.co");
  const [workspace, setWorkspace] = useState(user?.workspaceName || "Personal workspace");
  const [profileSaved, setProfileSaved] = useState(false);

  // Security state
  const [currentPass, setCurrentPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [passUpdated, setPassUpdated] = useState(false);
  const [twoFactor, setTwoFactor] = useState(true);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile({ name, email, workspaceName: workspace });
    setProfileSaved(true);
    setTimeout(() => setProfileSaved(false), 2500);
  };

  const handleUpdatePassword = (e: React.FormEvent) => {
    e.preventDefault();
    setPassUpdated(true);
    setCurrentPass("");
    setNewPass("");
    setConfirmPass("");
    setTimeout(() => setPassUpdated(false), 2500);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F6F8F7] dark:bg-[#10221F]">
      <Sidebar />

      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header title="Settings" badge="AI knowledge assistant" />

        <div className="flex-1 overflow-y-auto p-6 lg:p-10">
          <div className="max-w-3xl mx-auto space-y-6">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
                Settings
              </h1>
              <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
                Manage your profile, account preferences and workspace security.
              </p>
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center gap-2 border-b border-[#E5EBE8] dark:border-[#22423B] pb-3">
              <button
                onClick={() => setActiveTab("profile")}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === "profile"
                    ? "bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]"
                    : "text-[#6B7C77] dark:text-[#94A7A1] hover:text-[#172B28]"
                }`}
              >
                <User className="w-3.5 h-3.5" />
                <span>Profile</span>
              </button>

              <button
                onClick={() => setActiveTab("security")}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === "security"
                    ? "bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]"
                    : "text-[#6B7C77] dark:text-[#94A7A1] hover:text-[#172B28]"
                }`}
              >
                <Shield className="w-3.5 h-3.5" />
                <span>Security</span>
              </button>

              <button
                onClick={() => setActiveTab("preferences")}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === "preferences"
                    ? "bg-[#EAF4EF] dark:bg-[#1A3831] text-[#147D65] dark:text-[#4ADE80]"
                    : "text-[#6B7C77] dark:text-[#94A7A1] hover:text-[#172B28]"
                }`}
              >
                <Palette className="w-3.5 h-3.5" />
                <span>Preferences</span>
              </button>
            </div>

            {/* Tab 1: Profile (Screenshot 10) */}
            {activeTab === "profile" && (
              <div className="space-y-6">
                <form
                  onSubmit={handleSaveProfile}
                  className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs space-y-5"
                >
                  <h2 className="text-sm font-bold text-[#172B28] dark:text-[#F2F7F5]">
                    Profile details
                  </h2>

                  {/* Avatar upload */}
                  <div className="flex items-center gap-4">
                    <img
                      src={user?.avatarUrl}
                      alt={name}
                      className="w-14 h-14 rounded-full object-cover ring-2 ring-[#147D65]/20"
                    />
                    <div>
                      <button
                        type="button"
                        className="px-3 py-1.5 rounded-lg border border-[#E5EBE8] dark:border-[#28483F] text-xs font-medium text-[#172B28] dark:text-[#F2F7F5] hover:bg-[#F6F8F7] dark:hover:bg-[#1A3831] flex items-center gap-1.5"
                      >
                        <Upload className="w-3 h-3" />
                        <span>Upload photo</span>
                      </button>
                      <p className="text-[11px] text-[#8A9C96] mt-1">
                        JPG, PNG or GIF • Up to 2 MB
                      </p>
                    </div>
                  </div>

                  {/* Inputs */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                        Full name
                      </label>
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                        Email address
                      </label>
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                      Workspace name
                    </label>
                    <input
                      type="text"
                      value={workspace}
                      onChange={(e) => setWorkspace(e.target.value)}
                      className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    {profileSaved ? (
                      <span className="inline-flex items-center gap-1.5 text-xs text-[#147D65] dark:text-[#4ADE80] font-medium">
                        <CheckCircle2 className="w-4 h-4" /> Changes saved successfully!
                      </span>
                    ) : (
                      <span />
                    )}
                    <button
                      type="submit"
                      className="px-4 py-2 rounded-xl bg-[#147D65] hover:bg-[#0E634F] text-white text-xs font-medium shadow-xs"
                    >
                      Save changes
                    </button>
                  </div>
                </form>

                {/* Danger zone */}
                <div className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-red-200 dark:border-red-950/40 shadow-xs space-y-3">
                  <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                    <AlertTriangle className="w-4 h-4" />
                    <h3 className="text-xs font-bold uppercase tracking-wider">Danger Zone</h3>
                  </div>
                  <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                    Permanently delete your account and all associated documents, embeddings, and chat history.
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      if (confirm("Are you sure you want to sign out?")) {
                        logout();
                        window.location.href = "/login";
                      }
                    }}
                    className="px-4 py-2 rounded-xl bg-red-50 hover:bg-red-100 dark:bg-red-950/30 dark:hover:bg-red-900/40 text-red-600 dark:text-red-400 text-xs font-semibold"
                  >
                    Sign out / Delete account
                  </button>
                </div>
              </div>
            )}

            {/* Tab 2: Security (Screenshot 11) */}
            {activeTab === "security" && (
              <div className="space-y-6">
                <form
                  onSubmit={handleUpdatePassword}
                  className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs space-y-4"
                >
                  <h2 className="text-sm font-bold text-[#172B28] dark:text-[#F2F7F5]">
                    Change password
                  </h2>

                  <div>
                    <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                      Current password
                    </label>
                    <input
                      type="password"
                      required
                      value={currentPass}
                      onChange={(e) => setCurrentPass(e.target.value)}
                      className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5]"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                        New password
                      </label>
                      <input
                        type="password"
                        required
                        value={newPass}
                        onChange={(e) => setNewPass(e.target.value)}
                        className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5]"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
                        Confirm password
                      </label>
                      <input
                        type="password"
                        required
                        value={confirmPass}
                        onChange={(e) => setConfirmPass(e.target.value)}
                        className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5]"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    {passUpdated && (
                      <span className="inline-flex items-center gap-1.5 text-xs text-[#147D65] dark:text-[#4ADE80]">
                        <CheckCircle2 className="w-4 h-4" /> Password updated!
                      </span>
                    )}
                    <button
                      type="submit"
                      className="px-4 py-2 rounded-xl bg-[#147D65] text-white text-xs font-medium ml-auto"
                    >
                      Update password
                    </button>
                  </div>
                </form>

                {/* 2FA */}
                <div className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-bold text-[#172B28] dark:text-[#F2F7F5]">
                      Two-factor authentication
                    </h3>
                    <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-0.5">
                      Add an extra layer of security using an authenticator app.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setTwoFactor(!twoFactor)}
                    className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                      twoFactor ? "bg-[#147D65]" : "bg-gray-300 dark:bg-gray-700"
                    }`}
                  >
                    <div
                      className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                        twoFactor ? "translate-x-5" : ""
                      }`}
                    />
                  </button>
                </div>
              </div>
            )}

            {/* Tab 3: Preferences (Screenshot 12 - Theme selector) */}
            {activeTab === "preferences" && (
              <div className="space-y-6">
                <div className="p-6 rounded-2xl bg-white dark:bg-[#162E29] border border-[#E5EBE8] dark:border-[#26483F] shadow-xs space-y-4">
                  <h2 className="text-sm font-bold text-[#172B28] dark:text-[#F2F7F5]">
                    Appearance
                  </h2>
                  <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1]">
                    Customize how DocuMind looks on your device.
                  </p>

                  {/* 3 Theme Options */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                    {/* Light Option */}
                    <div
                      onClick={() => setTheme("light")}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        theme === "light"
                          ? "border-[#147D65] bg-[#EAF4EF]/30"
                          : "border-[#E5EBE8] dark:border-[#25463D] hover:border-[#147D65]/50"
                      }`}
                    >
                      <div className="h-20 rounded-lg bg-[#F6F8F7] border border-[#E5EBE8] p-2 flex flex-col justify-between mb-3 shadow-xs">
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 rounded-full bg-red-400" />
                          <div className="w-2 h-2 rounded-full bg-amber-400" />
                          <div className="w-2 h-2 rounded-full bg-green-400" />
                        </div>
                        <div className="w-full bg-white h-6 rounded flex items-center px-2 text-[9px] text-[#172B28] font-bold">
                          Light canvas
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Sun className="w-4 h-4 text-amber-500" />
                          <span className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                            Light
                          </span>
                        </div>
                        <input
                          type="radio"
                          name="theme"
                          checked={theme === "light"}
                          onChange={() => setTheme("light")}
                          className="text-[#147D65]"
                        />
                      </div>
                    </div>

                    {/* Dark Option */}
                    <div
                      onClick={() => setTheme("dark")}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        theme === "dark"
                          ? "border-[#147D65] dark:border-[#4ADE80] bg-[#147D65]/10"
                          : "border-[#E5EBE8] dark:border-[#25463D] hover:border-[#147D65]/50"
                      }`}
                    >
                      <div className="h-20 rounded-lg bg-[#10221F] border border-[#22423B] p-2 flex flex-col justify-between mb-3 shadow-xs">
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 rounded-full bg-red-400" />
                          <div className="w-2 h-2 rounded-full bg-amber-400" />
                          <div className="w-2 h-2 rounded-full bg-green-400" />
                        </div>
                        <div className="w-full bg-[#162E29] h-6 rounded flex items-center px-2 text-[9px] text-[#4ADE80] font-bold">
                          Dark forest
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Moon className="w-4 h-4 text-[#4ADE80]" />
                          <span className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                            Dark
                          </span>
                        </div>
                        <input
                          type="radio"
                          name="theme"
                          checked={theme === "dark"}
                          onChange={() => setTheme("dark")}
                          className="text-[#147D65]"
                        />
                      </div>
                    </div>

                    {/* System Option */}
                    <div
                      onClick={() => setTheme("system")}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        theme === "system"
                          ? "border-[#147D65] dark:border-[#4ADE80] bg-[#147D65]/10"
                          : "border-[#E5EBE8] dark:border-[#25463D] hover:border-[#147D65]/50"
                      }`}
                    >
                      <div className="h-20 rounded-lg bg-linear-to-r from-[#F6F8F7] to-[#10221F] border border-[#E5EBE8] dark:border-[#25463D] p-2 flex flex-col justify-between mb-3 shadow-xs">
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 rounded-full bg-red-400" />
                          <div className="w-2 h-2 rounded-full bg-amber-400" />
                          <div className="w-2 h-2 rounded-full bg-green-400" />
                        </div>
                        <div className="w-full bg-white/70 dark:bg-black/40 backdrop-blur-xs h-6 rounded flex items-center px-2 text-[9px] font-bold">
                          System sync
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Laptop className="w-4 h-4 text-blue-500" />
                          <span className="text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5]">
                            System
                          </span>
                        </div>
                        <input
                          type="radio"
                          name="theme"
                          checked={theme === "system"}
                          onChange={() => setTheme("system")}
                          className="text-[#147D65]"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
