import type { Metadata } from "next";
import { AnalyzeTabs } from "@/components/analyze-tabs";
import { AnalyzerForm } from "@/components/analyzer-form";
import { Card, CardContent } from "@/components/ui/card";

export const metadata: Metadata = { title: "Analyze email" };

export default function AnalyzePage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-4">
        <AnalyzeTabs />
        <div>
          <h1 className="text-2xl font-semibold">Analyze an email</h1>
          <p className="mt-1 text-sm text-muted-foreground">Paste the message exactly as you received it. Do not click any links in it.</p>
        </div>
      </div>
      <Card>
        <CardContent className="p-6">
          <AnalyzerForm />
        </CardContent>
      </Card>
    </div>
  );
}
