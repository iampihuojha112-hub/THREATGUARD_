import type { Metadata } from "next";
import { AnalyzeTabs } from "@/components/analyze-tabs";
import { AnalyzeUrlForm } from "@/components/analyze-url-form";
import { Card, CardContent } from "@/components/ui/card";

export const metadata: Metadata = { title: "Analyze URL" };

export default function AnalyzeUrlPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-4">
        <AnalyzeTabs />
        <div>
          <h1 className="text-2xl font-semibold">Analyze a URL</h1>
          <p className="mt-1 text-sm text-muted-foreground">Check a link before you open it. Do not visit it to test it.</p>
        </div>
      </div>
      <Card>
        <CardContent className="p-6">
          <AnalyzeUrlForm />
        </CardContent>
      </Card>
    </div>
  );
}
