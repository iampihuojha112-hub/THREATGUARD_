"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, ScanSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/services/api";

const MAX_URL = 2048;

export function AnalyzeUrlForm() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const value = url.trim();
    setApiError(null);
    if (!value) return setError("Paste the URL you want to check.");
    if (/\s/.test(value)) return setError("Enter one URL with no spaces.");
    if (value.length > MAX_URL) return setError(`The URL must be ${MAX_URL.toLocaleString()} characters or fewer.`);
    if (!value.includes(".")) return setError("The URL needs a domain, for example example.com/login.");
    setError(null);

    setLoading(true);
    try {
      const result = await api.analyzeUrl({ url: value });
      router.push(`/results/${result.id}`);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Analysis failed. Try again.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5" noValidate>
      <div className="space-y-2">
        <Label htmlFor="url">URL</Label>
        <Input
          id="url"
          type="text"
          inputMode="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="http://paypal-secure-login.example.xyz/verify"
          aria-invalid={!!error}
          aria-describedby={error ? "url-error" : "url-hint"}
          autoComplete="off"
          spellCheck={false}
        />
        {error ? (
          <p id="url-error" className="text-sm text-danger">
            {error}
          </p>
        ) : (
          <p id="url-hint" className="text-xs text-muted-foreground">
            Copy the link exactly as it appears, including http:// or https://. ThreatGuard reads the address only and never opens it.
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
        {loading ? "Analyzing..." : "Analyze URL"}
      </Button>
    </form>
  );
}
