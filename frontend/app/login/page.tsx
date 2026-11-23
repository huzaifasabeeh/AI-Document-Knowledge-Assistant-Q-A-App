"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { Eye, EyeOff, AlertCircle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const res = await login(email, password);
      if (res.success) {
        router.push("/");
      } else {
        setError(res.error || "Failed to sign in. Please verify your credentials.");
      }
    } catch {
      setError("Sign in failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleDemo = async () => {
    setIsSubmitting(true);
    await login("user@docmind.ai", "demo12345");
    router.push("/");
  };

  return (
    <AuthSplitLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[#172B28] dark:text-[#F2F7F5]">
            Welcome back
          </h2>
          <p className="text-xs text-[#6B7C77] dark:text-[#94A7A1] mt-1">
            Sign in to access your documents and private knowledge base.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/40 text-red-600 dark:text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Google SSO Button */}
        <button
          type="button"
          onClick={handleGoogleDemo}
          disabled={isSubmitting}
          className="w-full py-2.5 px-4 rounded-xl border border-[#E5EBE8] dark:border-[#26483F] hover:bg-[#F6F8F7] dark:hover:bg-[#162E29] flex items-center justify-center gap-2.5 text-xs font-semibold text-[#172B28] dark:text-[#F2F7F5] transition-colors"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          <span>Continue with Google</span>
        </button>

        {/* Divider */}
        <div className="relative flex items-center justify-center">
          <div className="border-t border-[#E5EBE8] dark:border-[#22423B] w-full" />
          <span className="bg-white dark:bg-[#10221F] px-3 text-[11px] text-[#8A9C96]">
            or continue with email
          </span>
        </div>

        {/* Email form */}
        <form onSubmit={handleSubmit} className="space-y-4">
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
                placeholder="Enter your password"
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
          </div>

          <div className="flex items-center justify-between text-xs pt-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="rounded text-[#147D65]"
              />
              <span className="text-[#6B7C77] dark:text-[#94A7A1]">Remember me</span>
            </label>
            <Link
              href="/forgot-password"
              className="font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
            >
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] disabled:opacity-50 text-white font-medium text-xs shadow-xs transition-colors"
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="text-center text-xs text-[#6B7C77] dark:text-[#94A7A1] pt-2">
          New to DocuMind?{" "}
          <Link
            href="/signup"
            className="font-medium text-[#147D65] dark:text-[#4ADE80] hover:underline"
          >
            Create an account
          </Link>
        </div>
      </div>
    </AuthSplitLayout>
  );
}
