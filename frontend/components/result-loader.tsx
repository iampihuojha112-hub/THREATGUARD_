"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ErrorState } from "@/components/error-state";
import { ResultView } from "@/components/result-view";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAsync } from "@/hooks/use-async";
import { SCAN_META } from "@/lib/scan-types";
import { api } from "@/services/api";

export function ResultLoader({ id }: { id: string }) {
  const { data, error, loading, reload } = useAsync(() => api.scan(id), [id]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Scan result</h1>
          <p className="mt-1 text-sm text-muted-foreground">Verdict, risk score and the signals behind it.</p>
        </div>
        <div className="flex gap-2">
          <Button asChild variant="outline" size="sm">
            <Link href="/history">
              <ArrowLeft className="h-4 w-4" /> History
            </Link>
          </Button>
          <Button asChild size="sm">
            <Link href={data ? SCAN_META[data.scan_type].href : "/analyze"}>Analyze another</Link>
          </Button>
        </div>
      </div>

      {error ? (
        <ErrorState message={error} onRetry={reload} />
      ) : loading || !data ? (
        <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
          <Skeleton className="h-[460px]" />
          <Skeleton className="h-[460px]" />
        </div>
      ) : (
        <ResultView result={data} />
      )}
    </div>
  );
}
