import { createClient } from "@/lib/supabase/client";
import type { AnalyzePayload, AnalyzeSmsPayload, AnalyzeUrlPayload, DashboardData, HistoryQuery, HistoryResponse, ScanResult } from "@/types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) {
    window.location.href = "/login";
    throw new ApiError("Your session has expired. Sign in again.", 401);
  }

  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
        ...(init.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError("Cannot reach the ThreatGuard API. Check that the backend is running.", 0);
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data.detail === "string") message = data.detail;
      else if (Array.isArray(data.detail) && data.detail[0]?.msg) {
        message = String(data.detail[0].msg).replace(/^Value error, /, "");
      }
    } catch {
      /* keep default message */
    }
    if (res.status === 401) {
      await supabase.auth.signOut();
      window.location.href = "/login";
    }
    throw new ApiError(message, res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  analyze: (payload: AnalyzePayload) =>
    request<ScanResult>("/api/analyze", { method: "POST", body: JSON.stringify(payload) }),

  analyzeUrl: (payload: AnalyzeUrlPayload) =>
    request<ScanResult>("/api/analyze/url", { method: "POST", body: JSON.stringify(payload) }),

  analyzeSms: (payload: AnalyzeSmsPayload) =>
    request<ScanResult>("/api/analyze/sms", { method: "POST", body: JSON.stringify(payload) }),

  history: (q: HistoryQuery) => {
    const params = new URLSearchParams({ page: String(q.page), page_size: String(q.pageSize), sort: q.sort });
    if (q.search.trim()) params.set("search", q.search.trim());
    if (q.prediction) params.set("prediction", q.prediction);
    if (q.scanType) params.set("scan_type", q.scanType);
    return request<HistoryResponse>(`/api/history?${params.toString()}`);
  },

  scan: (id: string) => request<ScanResult>(`/api/history/${encodeURIComponent(id)}`),

  dashboard: () => request<DashboardData>("/api/dashboard"),
};
