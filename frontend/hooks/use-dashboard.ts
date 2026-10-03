"use client";

import { api } from "@/services/api";
import { useAsync } from "./use-async";

export function useDashboard() {
  return useAsync(() => api.dashboard(), []);
}
