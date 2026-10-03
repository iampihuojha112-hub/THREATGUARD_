import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { SCAN_META, verdictLabel } from "@/lib/scan-types";
import { formatDateTime, formatPercent } from "@/lib/utils";
import type { RecentScan } from "@/types";

export function RecentActivity({ items }: { items: RecentScan[] }) {
  if (items.length === 0) {
    return <p className="py-10 text-center text-sm text-muted-foreground">Nothing scanned yet. Your latest results will appear here.</p>;
  }
  return (
    <ul className="divide-y">
      {items.map((scan) => {
        const Icon = SCAN_META[scan.scan_type].icon;
        return (
          <li key={scan.id}>
            <Link
              href={`/results/${scan.id}`}
              className="flex items-center gap-3 rounded-md px-1 py-2.5 transition-colors hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <Icon className="h-4 w-4 shrink-0 text-muted-foreground" aria-label={SCAN_META[scan.scan_type].label} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium" title={scan.title}>
                  {scan.title || "(no subject)"}
                </p>
                <p className="text-xs text-muted-foreground">{formatDateTime(scan.created_at)}</p>
              </div>
              <span className="text-sm tabular-nums text-muted-foreground">{formatPercent(scan.risk_score, 0)}</span>
              <Badge variant={scan.prediction === "phishing" ? "phishing" : "safe"}>{verdictLabel(scan.scan_type, scan.prediction)}</Badge>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
