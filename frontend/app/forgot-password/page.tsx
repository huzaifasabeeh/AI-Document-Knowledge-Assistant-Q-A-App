"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { Mail, ArrowLeft, CheckCircle2 } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("alex.morgan@acme.co");
  const [sent, setSent] = useState(true);

  const handleResend = (e: React.FormEvent) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <AuthSplitLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
            Check your inbox
          </h2>
          <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
            A little reset. A fresh start.
          </p>
        </div>

        {/* Mail Icon */}
        <div className="w-12 h-12 rounded-xl bg-[#EAF4EF] dark:bg-[#1C3B33] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80]">
          <Mail className="w-6 h-6" />
        </div>

        {/* Alert Banner (Screenshot 9) */}
        {sent && (
          <div className="p-4 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] space-y-1">
            <div className="text-xs font-bold text-[#147D65] dark:text-[#4ADE80]">
              Reset link sent
            </div>
            <p className="text-xs text-[#264E43] dark:text-[#CFDFD9] leading-relaxed">
              We&apos;ve sent password reset instructions to your email. The link is valid for 30 minutes.
            </p>
          </div>
        )}

        <form onSubmit={handleResend} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              Email address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] text-white font-medium text-xs shadow-xs transition-colors"
          >
            Resend reset link
          </button>
        </form>

        <div className="text-center pt-2">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to sign in</span>
          </Link>
        </div>
      </div>
    </AuthSplitLayout>
  );
}
