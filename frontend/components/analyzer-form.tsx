"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, ScanSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/services/api";

const EMAIL_RE = /[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}/;
const MAX_BODY = 50000;

export function AnalyzerForm() {
  const router = useRouter();
  const [subject, setSubject] = useState("");
  const [sender, setSender] = useState("");
  const [body, setBody] = useState("");
  const [errors, setErrors] = useState<{ sender?: string; body?: string }>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const next: typeof errors = {};
    if (!EMAIL_RE.test(sender)) next.sender = "Enter the sender's email address, for example billing@company.com.";
    if (!body.trim()) next.body = "Paste the email body to analyze.";
    if (body.length > MAX_BODY) next.body = `The body must be ${MAX_BODY.toLocaleString()} characters or fewer.`;
    setErrors(next);
    setApiError(null);
    if (Object.keys(next).length) return;

    setLoading(true);
    try {
      const result = await api.analyze({ subject: subject.trim(), sender: sender.trim(), body: body.trim() });
      router.push(`/results/${result.id}`);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Analysis failed. Try again.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5" noValidate>
      <div className="space-y-2">
        <Label htmlFor="subject">Subject</Label>
        <Input id="subject" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Action required: confirm your account" maxLength={998} />
      </div>

      <div className="space-y-2">
        <Label htmlFor="sender">Sender email</Label>
        <Input
          id="sender"
          type="text"
          inputMode="email"
          value={sender}
          onChange={(e) => setSender(e.target.value)}
          placeholder="support@paypa1-secure.xyz"
          aria-invalid={!!errors.sender}
          aria-describedby={errors.sender ? "sender-error" : undefined}
          autoComplete="off"
        />
        {errors.sender && (
          <p id="sender-error" className="text-sm text-danger">
            {errors.sender}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-baseline justify-between">
          <Label htmlFor="body">Email body</Label>
          <span className="text-xs tabular-nums text-muted-foreground">{body.length.toLocaleString()} / {MAX_BODY.toLocaleString()}</span>
        </div>
        <Textarea
          id="body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Paste the full email text, including any links."
          className="min-h-[240px]"
          aria-invalid={!!errors.body}
          aria-describedby={errors.body ? "body-error" : undefined}
        />
        {errors.body && (
          <p id="body-error" className="text-sm text-danger">
            {errors.body}
          </p>
        )}
      </div>

      {apiError && (
        <div role="alert" className="rounded-md border border-danger/30 bg-danger/10 p-3 text-sm text-danger">
          {apiError}
        </div>
      )}

      <Button type="submit" size="lg" disabled={loading} className="w-full sm:w-auto">
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ScanSearch className="h-4 w-4" />}
        {loading ? "Analyzing..." : "Analyze email"}
      </Button>
    </form>
  );
}
