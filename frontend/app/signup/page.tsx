"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";
import { Eye, EyeOff, Check } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [name, setName] = useState("Alex Morgan");
  const [email, setEmail] = useState("alex.morgan@acme.co");
  const [password, setPassword] = useState("P@ssw0rd2026!");
  const [confirmPass, setConfirmPass] = useState("P@ssw0rd2026!");
  const [showPass, setShowPass] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await signup(name, email, password);
    router.push("/");
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

        {/* Google SSO */}
        <button
          type="button"
          onClick={() => {
            signup(name, email, password);
            router.push("/");
          }}
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

        <div className="relative flex items-center justify-center">
          <div className="border-t border-[#E5EBE8] dark:border-[#22423B] w-full" />
          <span className="bg-white dark:bg-[#10221F] px-3 text-[11px] text-[#8A9C96]">
            or continue with email
          </span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              Full name
            </label>
            <input
              type="text"
              required
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
            <div className="flex items-center gap-1.5 text-[11px] text-[#147D65] dark:text-[#4ADE80] mt-1.5">
              <Check className="w-3.5 h-3.5" />
              <span>Strong password • 8+ characters, number and symbol</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[#172B28] dark:text-[#E2EBE7] mb-1">
              Confirm password
            </label>
            <input
              type={showPass ? "text" : "password"}
              required
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
            className="w-full py-2.5 rounded-xl bg-[#147D65] hover:bg-[#0E634F] text-white font-medium text-xs shadow-xs transition-colors"
          >
            Create account
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
