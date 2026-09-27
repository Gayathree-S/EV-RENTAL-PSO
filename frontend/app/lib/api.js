/**
 * API client helper for backend communication.
 * Uses native fetch with NEXT_PUBLIC_API_URL fallback.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    let data;
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMessage =
        (data && data.detail) ||
        (typeof data === "string" ? data : `Request failed with status ${response.status}`);
      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (err) {
    if (err.name === "TypeError" && err.message.includes("fetch")) {
      throw new Error(
        `Unable to reach backend server at ${API_BASE_URL}. Ensure FastAPI is running on port 8000.`
      );
    }
    throw err;
  }
}

export const api = {
  get: (endpoint, options) => apiRequest(endpoint, { method: "GET", ...options }),
  post: (endpoint, body, options) =>
    apiRequest(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
      ...options,
    }),
};
