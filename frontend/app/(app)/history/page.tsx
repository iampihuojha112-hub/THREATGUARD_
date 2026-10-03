import type { Metadata } from "next";
import { HistoryTable } from "@/components/history-table";

export const metadata: Metadata = { title: "Scan history" };

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Scan history</h1>
        <p className="mt-1 text-sm text-muted-foreground">Every email you have analyzed. Select a row to see its full result.</p>
      </div>
      <HistoryTable />
    </div>
  );
}
