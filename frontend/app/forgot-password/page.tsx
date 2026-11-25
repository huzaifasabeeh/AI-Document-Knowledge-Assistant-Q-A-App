"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { AlertCircle, ArrowLeft, CheckCircle2, Mail } from "lucide-react";
import { requestRecovery } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sentMessage, setSentMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSentMessage(null);
    setIsSubmitting(true);
    try {
      const res = await requestRecovery(email);
      setSentMessage(res.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send reset code.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthSplitLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
            Forgot your password?
          </h2>
          <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
            We will email a one-time numeric code. Enter it with your new password on the next step.
          </p>
        </div>

        <div className="w-11 h-11 rounded-xl bg-[#EAF4EF] dark:bg-[#1C3B33] flex items-center justify-center text-[#147D65] dark:text-[#4ADE80]">
          <Mail className="w-5 h-5" />
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-red-700 dark:text-red-400 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {sentMessage && (
          <div className="p-4 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] space-y-2.5">
            <div className="flex items-start gap-2 text-xs font-medium text-[#147D65] dark:text-[#4ADE80]">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{sentMessage}</span>
            </div>
            <Link
              href={`/reset-password?email=${encodeURIComponent(email.trim())}`}
              className="w-full block text-center py-2 rounded-lg bg-[#147D65] hover:bg-[#0E634F] text-white font-medium text-xs transition-colors"
            >
              Enter code &amp; set new password →
            </Link>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="recovery-email"
              className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
            >
              Email
            </label>
            <input
              id="recovery-email"
              type="email"
              required
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              disabled={isSubmitting}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-50 text-white font-medium text-xs shadow-xs transition-colors"
          >
            {isSubmitting ? "Sending code…" : "Send reset code"}
          </button>
        </form>

        <div className="flex items-center justify-between text-xs pt-2">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Log in</span>
          </Link>
          <Link
            href="/reset-password"
            className="font-medium text-[#6B7C77] dark:text-[#94A7A1] hover:text-[#172B28] dark:hover:text-white"
          >
            Already have a code?
          </Link>
        </div>
      </div>
    </AuthSplitLayout>
  );
}
