"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "../lib/api";
import { setStoredUser } from "../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
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
      const data = await api.post("/auth/login", formData);
      // NOTE: Storing user details directly in localStorage ("ev_user") is a
      // deliberate design simplification for this academic demonstration project.
      // In production environments, HTTP-only secure cookies with JWT tokens are standard.
      setStoredUser({
        user_id: data.user_id,
        name: data.name,
        email: data.email,
        is_admin: data.is_admin,
      });
      if (data.is_admin) {
        router.push("/admin");
      } else {
        router.push("/centers");
      }
    } catch (err) {
      setError(err.message || "Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md">

        {/* Logo / brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-600 shadow-lg mb-4">
            <span className="text-2xl">⚡</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Sign in
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Access your EV rental account
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">

          {/* Error banner */}
          {error && (
            <div className="mb-5 flex items-start gap-3 p-4 rounded-xl bg-red-50 border border-red-200">
              <span className="text-red-500 text-base mt-0.5 shrink-0">✕</span>
              <p className="text-sm text-red-700 leading-snug">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
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
                  autoComplete="current-password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
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
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-semibold text-sm transition-all shadow-sm disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2 mt-2"
            >
              {loading ? (
                <>
                  <span className="inline-block w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Signing in…
                </>
              ) : (
                "Sign in"
              )}
            </button>
          </form>
        </div>

        {/* Register link */}
        <p className="mt-6 text-center text-sm text-slate-500">
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            className="font-semibold text-emerald-600 hover:text-emerald-700 hover:underline transition-colors"
          >
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
