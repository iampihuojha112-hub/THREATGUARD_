import type { Metadata } from "next";
import { AnalyzeSmsForm } from "@/components/analyze-sms-form";
import { AnalyzeTabs } from "@/components/analyze-tabs";
import { Card, CardContent } from "@/components/ui/card";

export const metadata: Metadata = { title: "Analyze SMS" };

export default function AnalyzeSmsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-4">
        <AnalyzeTabs />
        <div>
          <h1 className="text-2xl font-semibold">Analyze a text message</h1>
          <p className="mt-1 text-sm text-muted-foreground">Paste a suspicious SMS. Do not reply to it or call any number in it.</p>
        </div>
      </div>
      <Card>
        <CardContent className="p-6">
          <AnalyzeSmsForm />
        </CardContent>
      </Card>
    </div>
  );
}
