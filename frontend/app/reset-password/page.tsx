"use client";

import React, { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { AlertCircle, ArrowLeft, CheckCircle2, Eye, EyeOff } from "lucide-react";
import { resetPassword } from "@/lib/api";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const initialEmail = searchParams.get("email") || "";

  const [email, setEmail] = useState(initialEmail);
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    const normalizedCode = code.replace(/\s+/g, "");
    if (!/^\d{6,10}$/.test(normalizedCode)) {
      setError("Enter the numeric code from the email.");
      return;
    }
    if (password.length < 8) {
      setError("Use a password with at least 8 characters.");
      return;
    }
    if (password !== confirmation) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await resetPassword(email, normalizedCode, password, confirmation);
      setSuccessMsg(res.message);
      setCode("");
      setPassword("");
      setConfirmation("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Password reset failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
          Set a new password
        </h2>
        <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
          Enter the one-time numeric code emailed to you along with a new password.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-red-700 dark:text-red-400 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] space-y-2.5">
          <div className="flex items-start gap-2 text-xs font-medium text-[#147D65] dark:text-[#4ADE80]">
            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{successMsg}</span>
          </div>
          <Link
            href="/login"
            className="w-full block text-center py-2 rounded-lg bg-[#147D65] hover:bg-[#0E634F] text-white font-medium text-xs transition-colors"
          >
            Back to Log in
          </Link>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="reset-email"
            className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
          >
            Email
          </label>
          <input
            id="reset-email"
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

        <div>
          <label
            htmlFor="reset-code"
            className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
          >
            Code from email
          </label>
          <input
            id="reset-code"
            type="text"
            inputMode="numeric"
            required
            placeholder="6–10 digit recovery code"
            value={code}
            disabled={isSubmitting}
            onChange={(e) => setCode(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
          />
        </div>

        <div>
          <label
            htmlFor="reset-password"
            className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
          >
            New password
          </label>
          <div className="relative">
            <input
              id="reset-password"
              type={showPass ? "text" : "password"}
              required
              autoComplete="new-password"
              placeholder="At least 8 characters"
              value={password}
              disabled={isSubmitting}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2.5 pr-9 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
            />
            <button
              type="button"
              onClick={() => setShowPass(!showPass)}
              aria-label={showPass ? "Hide password" : "Show password"}
              className="absolute right-2.5 top-2.5 text-[#8A9C96] hover:text-[#172B28] dark:hover:text-white"
            >
              {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div>
          <label
            htmlFor="reset-confirm"
            className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
          >
            Confirm new password
          </label>
          <input
            id="reset-confirm"
            type={showPass ? "text" : "password"}
            required
            autoComplete="new-password"
            placeholder="Re-enter new password"
            value={confirmation}
            disabled={isSubmitting}
            onChange={(e) => setConfirmation(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-50 text-white font-medium text-xs shadow-xs transition-colors"
        >
          {isSubmitting ? "Updating password…" : "Set new password"}
        </button>
      </form>

      <div className="text-center pt-2">
        <Link
          href="/login"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Log in</span>
        </Link>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <AuthSplitLayout>
      <Suspense fallback={<div className="text-xs text-[#6B7C77]">Loading…</div>}>
        <ResetPasswordForm />
      </Suspense>
    </AuthSplitLayout>
  );
}
