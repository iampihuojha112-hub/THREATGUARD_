"use client";

import Link from "next/link";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/error-state";
import { useHistory } from "@/hooks/use-history";
import { SCAN_META, SCAN_TYPES, verdictLabel } from "@/lib/scan-types";
import { cn, formatDateTime, formatPercent } from "@/lib/utils";
import type { HistoryQuery } from "@/types";

const selectClass =
  "h-10 rounded-md border border-input bg-muted/60 px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export function HistoryTable() {
  const h = useHistory();
  const { data, loading, error, query } = h;

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={h.searchInput} onChange={(e) => h.setSearchInput(e.target.value)} placeholder="Search by subject, URL, message or sender" className="pl-9" aria-label="Search scans" />
        </div>
        <select className={selectClass} value={query.scanType} onChange={(e) => h.setScanType(e.target.value as HistoryQuery["scanType"])} aria-label="Filter by type">
          <option value="">All types</option>
          {SCAN_TYPES.map((t) => (
            <option key={t} value={t}>
              {SCAN_META[t].label}
            </option>
          ))}
        </select>
        <select className={selectClass} value={query.prediction} onChange={(e) => h.setPrediction(e.target.value as HistoryQuery["prediction"])} aria-label="Filter by result">
          <option value="">All results</option>
          <option value="phishing">Threats only</option>
          <option value="safe">Safe</option>
        </select>
        <select className={selectClass} value={query.sort} onChange={(e) => h.setSort(e.target.value as HistoryQuery["sort"])} aria-label="Sort scans">
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
          <option value="risk_desc">Highest risk</option>
          <option value="risk_asc">Lowest risk</option>
        </select>
      </div>

      {error ? (
        <ErrorState message={error} onRetry={h.reload} />
      ) : (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-left text-sm">
              <thead className="border-b bg-muted/40 text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Content</th>
                  <th className="px-4 py-3 font-medium">Sender</th>
                  <th className="px-4 py-3 font-medium">Result</th>
                  <th className="px-4 py-3 text-right font-medium">Risk</th>
                  <th className="px-4 py-3 text-right font-medium">Confidence</th>
                  <th className="px-4 py-3 font-medium">Scanned</th>
                </tr>
              </thead>
              <tbody>
                {loading &&
                  !data &&
                  Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i} className="border-b last:border-0">
                      <td colSpan={7} className="px-4 py-3">
                        <Skeleton className="h-6 w-full" />
                      </td>
                    </tr>
                  ))}
                {data?.items.map((scan) => (
                  <tr key={scan.id} className={cn("border-b transition-colors last:border-0 hover:bg-accent/40", loading && "opacity-60")}>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center gap-1.5 text-muted-foreground">
                        {(() => {
                          const Icon = SCAN_META[scan.scan_type].icon;
                          return <Icon className="h-4 w-4" />;
                        })()}
                        {SCAN_META[scan.scan_type].label}
                      </span>
                    </td>
                    <td className="max-w-[260px] px-4 py-3">
                      <Link href={`/results/${scan.id}`} className="block truncate font-medium hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" title={scan.title}>
                        {scan.title || "(no subject)"}
                      </Link>
                    </td>
                    <td className="max-w-[220px] truncate px-4 py-3 text-muted-foreground" title={scan.sender}>
                      {scan.sender || "-"}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={scan.prediction === "phishing" ? "phishing" : "safe"} className="capitalize">
                        {verdictLabel(scan.scan_type, scan.prediction)}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums">{formatPercent(scan.risk_score)}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{formatPercent(scan.confidence_score)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">{formatDateTime(scan.created_at)}</td>
                  </tr>
                ))}
                {data && data.items.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-14 text-center text-muted-foreground">
                      {query.search || query.prediction || query.scanType ? (
                        "No scans match these filters. Clear the search or choose All results."
                      ) : (
                        <>
                          No scans yet.{" "}
                          <Link href="/analyze" className="text-primary underline underline-offset-4">
                            Analyze your first email, URL or message
                          </Link>
                          .
                        </>
                      )}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {data && data.total > 0 && (
            <div className="flex flex-col items-center justify-between gap-3 border-t px-4 py-3 text-sm sm:flex-row">
              <p className="text-muted-foreground">
                Showing {(data.page - 1) * data.page_size + 1} to {Math.min(data.page * data.page_size, data.total)} of {data.total}
              </p>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled={data.page <= 1 || loading} onClick={() => h.setPage(data.page - 1)}>
                  <ChevronLeft className="h-4 w-4" /> Previous
                </Button>
                <span className="px-2 tabular-nums text-muted-foreground">
                  Page {data.page} of {data.total_pages}
                </span>
                <Button variant="outline" size="sm" disabled={data.page >= data.total_pages || loading} onClick={() => h.setPage(data.page + 1)}>
                  Next <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
