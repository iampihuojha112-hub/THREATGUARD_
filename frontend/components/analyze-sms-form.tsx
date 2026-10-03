"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, ScanSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/services/api";

const MAX_MESSAGE = 1600;

export function AnalyzeSmsForm() {
  const router = useRouter();
  const [sender, setSender] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setApiError(null);
    if (!message.trim()) return setError("Paste the text message to analyze.");
    if (message.length > MAX_MESSAGE) return setError(`The message must be ${MAX_MESSAGE.toLocaleString()} characters or fewer.`);
    setError(null);

    setLoading(true);
    try {
      const result = await api.analyzeSms({ message: message.trim(), sender: sender.trim() });
      router.push(`/results/${result.id}`);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Analysis failed. Try again.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5" noValidate>
      <div className="space-y-2">
        <Label htmlFor="sms-sender">Sender (optional)</Label>
        <Input id="sms-sender" value={sender} onChange={(e) => setSender(e.target.value)} placeholder="+91 98765 43210 or VM-HDFCBK" maxLength={40} autoComplete="off" />
      </div>

      <div className="space-y-2">
        <div className="flex items-baseline justify-between">
          <Label htmlFor="sms-message">Message</Label>
          <span className="text-xs tabular-nums text-muted-foreground">
            {message.length.toLocaleString()} / {MAX_MESSAGE.toLocaleString()}
          </span>
        </div>
        <Textarea
          id="sms-message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Paste the full text of the message, including any links or phone numbers."
          className="min-h-[180px]"
          aria-invalid={!!error}
          aria-describedby={error ? "sms-error" : undefined}
        />
        {error && (
          <p id="sms-error" className="text-sm text-danger">
            {error}
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
        {loading ? "Analyzing..." : "Analyze message"}
      </Button>
    </form>
  );
}
