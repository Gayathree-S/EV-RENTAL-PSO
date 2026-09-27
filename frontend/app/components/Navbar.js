"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { getStoredUser, clearStoredUser } from "../lib/auth";

export default function Navbar() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  const pathname = usePathname();

  const syncUser = () => {
    setUser(getStoredUser());
  };

  useEffect(() => {
    syncUser();
    window.addEventListener("storage", syncUser);
    return () => window.removeEventListener("storage", syncUser);
  }, [pathname]);

  const handleLogout = () => {
    clearStoredUser();
    setUser(null);
    router.push("/login");
  };

  return (
    <header className="border-b border-gray-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link
            href={user ? "/centers" : "/"}
            className="text-xl font-bold tracking-tight text-emerald-600 flex items-center gap-2 hover:opacity-90"
          >
            <span>⚡</span>
            <span>Smart EV Rental</span>
          </Link>

          {user && (
            <nav className="hidden sm:flex items-center gap-4">
              <Link
                href="/centers"
                className={`text-sm font-medium transition-colors ${
                  pathname === "/centers"
                    ? "text-emerald-600 font-semibold"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Rental Centers
              </Link>
              {user.is_admin && (
                <Link
                  href="/admin"
                  className={`text-sm font-medium transition-colors ${
                    pathname === "/admin"
                      ? "text-purple-600 font-semibold"
                      : "text-gray-600 hover:text-purple-700"
                  }`}
                >
                  Admin Dashboard
                </Link>
              )}
            </nav>
          )}
        </div>

        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600 hidden sm:inline">
                Welcome, <span className="font-semibold text-gray-900">{user.name}</span>
                {user.is_admin && (
                  <span className="ml-2 px-2 py-0.5 text-xs font-semibold bg-purple-100 text-purple-700 rounded-full">
                    Admin
                  </span>
                )}
              </span>
              <button
                onClick={handleLogout}
                className="px-3.5 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors border border-red-200 cursor-pointer"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="px-3.5 py-1.5 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="px-3.5 py-1.5 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors shadow-sm"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
