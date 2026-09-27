"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "../lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/auth/register", formData);
      setSuccess(true);
      setTimeout(() => router.push("/login"), 1500);
    } catch (err) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center py-8 px-4">
      <div className="w-full max-w-md">

        {/* Logo / brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-600 shadow-lg mb-4">
            <span className="text-2xl">⚡</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Create account
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Join to book EVs across our grid-optimized network
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">

          {/* Error */}
          {error && (
            <div className="mb-5 flex items-start gap-3 p-4 rounded-xl bg-red-50 border border-red-200">
              <span className="text-red-500 text-base mt-0.5 shrink-0">✕</span>
              <p className="text-sm text-red-700 leading-snug">{error}</p>
            </div>
          )}

          {/* Success */}
          {success && (
            <div className="mb-5 flex items-start gap-3 p-4 rounded-xl bg-emerald-50 border border-emerald-200">
              <span className="text-emerald-500 text-base mt-0.5 shrink-0">✓</span>
              <p className="text-sm text-emerald-700 leading-snug">
                Account created! Redirecting to sign in…
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name */}
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-semibold text-slate-700 mb-1.5"
              >
                Full name
              </label>
              <input
                id="name"
                type="text"
                name="name"
                required
                autoComplete="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Jane Smith"
                style={{ color: "#0f172a", backgroundColor: "#ffffff" }}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-slate-900 bg-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition"
              />
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-semibold text-slate-700 mb-1.5"
              >
                Email address
              </label>
              <input
                id="email"
                type="email"
                name="email"
                required
                autoComplete="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                style={{ color: "#0f172a", backgroundColor: "#ffffff" }}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-slate-900 bg-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-semibold text-slate-700 mb-1.5"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  name="password"
                  required
                  autoComplete="new-password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Choose a strong password"
                  style={{ color: "#0f172a", backgroundColor: "#ffffff" }}
                  className="w-full px-4 py-2.5 pr-12 rounded-xl border border-slate-300 text-slate-900 bg-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition"
                />
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-sm select-none cursor-pointer"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "🙈" : "👁️"}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading || success}
              className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-semibold text-sm transition-all shadow-sm disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2 mt-2"
            >
              {loading ? (
                <>
                  <span className="inline-block w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Creating account…
                </>
              ) : (
                "Create account"
              )}
            </button>
          </form>
        </div>

        {/* Login link */}
        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-semibold text-emerald-600 hover:text-emerald-700 hover:underline transition-colors"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
