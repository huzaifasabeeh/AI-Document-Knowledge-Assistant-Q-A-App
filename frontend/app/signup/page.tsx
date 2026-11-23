"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { Eye, EyeOff, Check, AlertCircle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !password.trim()) {
      setError("Please fill in all required fields.");
      return;
    }
    if (password !== confirmPass) {
      setError("Passwords do not match. Please try again.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (!agreeTerms) {
      setError("You must agree to the Terms of Service.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const res = await signup(name, email, password);
      if (res.success) {
        router.push("/");
      } else {
        setError(res.error || "Failed to create account.");
      }
    } catch {
      setError("Account creation failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthSplitLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
            Make room for clarity
          </h2>
          <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
            Start building your personal knowledge workspace.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-red-600 dark:text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              Full name
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Huzaifa Sabeeh"
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
              required
              placeholder="name@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              Password
            </label>
            <div className="relative">
              <input
                type={showPass ? "text" : "password"}
                required
                placeholder="At least 8 characters"
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
            {password.length >= 8 && (
              <div className="flex items-center gap-1.5 text-[11px] text-[#147D65] dark:text-[#4ADE80] mt-1.5">
                <Check className="w-3.5 h-3.5" />
                <span>Strong password • 8+ characters</span>
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              Confirm password
            </label>
            <input
              type={showPass ? "text" : "password"}
              required
              placeholder="Re-enter password"
              value={confirmPass}
              onChange={(e) => setConfirmPass(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-[#E5EBE8] dark:border-[#25463D] bg-transparent text-xs text-[#172B28] dark:text-[#F2F7F5] focus:outline-hidden focus:ring-1 focus:ring-[#147D65]"
            />
          </div>

          <label className="flex items-center gap-2 text-xs pt-1 cursor-pointer">
            <input
              type="checkbox"
              required
              checked={agreeTerms}
              onChange={(e) => setAgreeTerms(e.target.checked)}
              className="rounded text-[#147D65]"
            />
            <span className="text-[#6B7C77] dark:text-[#94A7A1]">
              I agree to the Terms of Service and Privacy Policy.
            </span>
          </label>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-50 text-white font-medium text-xs shadow-xs transition-colors"
          >
            {isSubmitting ? "Creating account..." : "Create account"}
          </button>
        </form>

        <div className="text-center text-xs text-[#6B7C77] dark:text-[#94A7A1] pt-2">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
          >
            Sign in
          </Link>
        </div>
      </div>
    </AuthSplitLayout>
  );
}
