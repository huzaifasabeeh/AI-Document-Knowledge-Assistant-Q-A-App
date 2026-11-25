"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { AlertCircle, CheckCircle2, Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function SignupPage() {
  const router = useRouter();
  const { signup, isAuthenticated, isLoading, health, healthError } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/");
    }
  }, [isAuthenticated, isLoading, router]);

  const authBlocked = Boolean(healthError || (health && !health.auth_configured));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (authBlocked) return;
    setError(null);
    setSuccessMsg(null);

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
      const msg = await signup(email, password, confirmation);
      setSuccessMsg(msg);
      setPassword("");
      setConfirmation("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create account.");
      setPassword("");
      setConfirmation("");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthSplitLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
            Create account
          </h2>
          <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
            Register an email and password. You must confirm your email if required before logging in.
          </p>
        </div>

        {authBlocked && (
          <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-300 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>
              {healthError ||
                health?.auth_error ||
                "Account sign-in is not configured yet. Please contact the app owner."}
            </span>
          </div>
        )}

        {error && (
          <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-red-700 dark:text-red-400 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="p-4 rounded-xl bg-[#EAF4EF] dark:bg-[#1A3831] border border-[#C8E2D5] dark:border-[#274F44] space-y-2">
            <div className="flex items-start gap-2 text-xs text-[#147D65] dark:text-[#4ADE80] font-medium">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{successMsg}</span>
            </div>
            <Link
              href="/login"
              className="inline-block text-xs font-semibold text-[#147D65] dark:text-[#4ADE80] hover:underline"
            >
              Go to Log in →
            </Link>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="signup-email"
              className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
            >
              Email
            </label>
            <input
              id="signup-email"
              type="email"
              required
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              disabled={authBlocked || isSubmitting}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65] disabled:opacity-50"
            />
          </div>

          <div>
            <label
              htmlFor="signup-password"
              className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
            >
              Password
            </label>
            <div className="relative">
              <input
                id="signup-password"
                type={showPass ? "text" : "password"}
                required
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={password}
                disabled={authBlocked || isSubmitting}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-2.5 pr-9 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65] disabled:opacity-50"
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
              htmlFor="signup-confirm"
              className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1"
            >
              Confirm password
            </label>
            <input
              id="signup-confirm"
              type={showPass ? "text" : "password"}
              required
              autoComplete="new-password"
              placeholder="Re-enter password"
              value={confirmation}
              disabled={authBlocked || isSubmitting}
              onChange={(e) => setConfirmation(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] placeholder-[#8A9C96] focus:outline-hidden focus:ring-1 focus:ring-[#147D65] disabled:opacity-50"
            />
          </div>

          <button
            type="submit"
            disabled={authBlocked || isSubmitting}
            className="w-full py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-50 text-white font-medium text-xs shadow-xs transition-colors"
          >
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <div className="text-center text-xs text-[#6B7C77] dark:text-[#94A7A1] pt-2">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
          >
            Log in
          </Link>
        </div>
      </div>
    </AuthSplitLayout>
  );
}
