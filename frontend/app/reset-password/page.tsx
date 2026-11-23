"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { Eye, EyeOff, Check, CheckCircle2 } from "lucide-react";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("••••••••••••");
  const [confirmPass, setConfirmPass] = useState("••••••••••••");
  const [showPass, setShowPass] = useState(false);
  const [updated, setUpdated] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUpdated(true);
    setTimeout(() => router.push("/login"), 2000);
  };

  return (
    <AuthSplitLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
            Set a new password
          </h2>
          <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
            Make it strong. Make it yours.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              New password
            </label>
            <div className="relative">
              <input
                type={showPass ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-2.5 pr-9 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-2.5 top-2.5 text-[#8A9C96] hover:text-[#172B28]"
              >
                {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <div className="flex items-center gap-3 text-[11px] text-[#147D65] dark:text-[#4ADE80] mt-1.5">
              <span className="inline-flex items-center gap-1">
                <Check className="w-3 h-3" /> At least 8 characters
              </span>
              <span className="inline-flex items-center gap-1">
                <Check className="w-3 h-3" /> A number and a symbol
              </span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              Confirm new password
            </label>
            <input
              type={showPass ? "text" : "password"}
              required
              value={confirmPass}
              onChange={(e) => setConfirmPass(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
            />
          </div>

          {/* Success Banner (Screenshot 8) */}
          {updated && (
            <div className="p-4 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-[#147D65] dark:text-[#4ADE80]">
                <CheckCircle2 className="w-4 h-4" />
                <span>Password updated successfully</span>
              </div>
              <p className="text-xs text-[#264E43] dark:text-[#CFDFD9] leading-relaxed">
                You can now sign in with your new password.
              </p>
            </div>
          )}

          <Link
            href="/login"
            className="w-full block text-center py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] text-white font-medium text-xs shadow-xs transition-colors"
          >
            Back to sign in
          </Link>
        </form>

        <p className="text-[11px] text-[#8A9C96] text-center">
          For your security, other sessions have been signed out.
        </p>
      </div>
    </AuthSplitLayout>
  );
}
