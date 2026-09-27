/**
 * Auth and session helper.
 *
 * NOTE: This uses localStorage ("ev_user") for demo-only session state.
 * This is a simplified approach tailored for academic demonstration,
 * matching Task 9's backend auth without JWT tokens or refresh flows.
 */

export const AUTH_STORAGE_KEY = "ev_user";

export function getStoredUser() {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(userData) {
  if (typeof window === "undefined") return;
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(userData));
  // Dispatch storage event so components can update in real-time
  window.dispatchEvent(new Event("storage"));
}

export function clearStoredUser() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(AUTH_STORAGE_KEY);
  window.dispatchEvent(new Event("storage"));
}
