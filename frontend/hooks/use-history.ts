"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/api";
import type { HistoryQuery } from "@/types";
import { useAsync } from "./use-async";

export function useHistory(initial?: Partial<HistoryQuery>) {
  const [query, setQuery] = useState<HistoryQuery>({
    page: 1,
    pageSize: 10,
    search: "",
    prediction: "",
    scanType: "",
    sort: "newest",
    ...initial,
  });
  const [searchInput, setSearchInput] = useState("");

  // Debounce search input
  useEffect(() => {
    const t = setTimeout(() => {
      setQuery((q) => (q.search === searchInput ? q : { ...q, search: searchInput, page: 1 }));
    }, 350);
    return () => clearTimeout(t);
  }, [searchInput]);

  const state = useAsync(() => api.history(query), [query.page, query.pageSize, query.search, query.prediction, query.scanType, query.sort]);

  return {
    ...state,
    query,
    searchInput,
    setSearchInput,
    setPage: (page: number) => setQuery((q) => ({ ...q, page })),
    setPrediction: (prediction: HistoryQuery["prediction"]) => setQuery((q) => ({ ...q, prediction, page: 1 })),
    setScanType: (scanType: HistoryQuery["scanType"]) => setQuery((q) => ({ ...q, scanType, page: 1 })),
    setSort: (sort: HistoryQuery["sort"]) => setQuery((q) => ({ ...q, sort, page: 1 })),
  };
}
