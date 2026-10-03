import { AlertOctagon, CheckCircle2, Clock, Link2, ShieldAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { RiskGauge } from "@/components/risk-gauge";
import { SCAN_META } from "@/lib/scan-types";
import { cn, formatDateTime, formatPercent } from "@/lib/utils";
import type { ScanResult, Severity } from "@/types";

const SEVERITY_STYLE: Record<Severity, string> = {
  high: "border-danger/30 bg-danger/10",
  medium: "border-warn/30 bg-warn/10",
  low: "border-border bg-muted/50",
};
const SEVERITY_BADGE: Record<Severity, "phishing" | "warn" | "outline"> = { high: "phishing", medium: "warn", low: "outline" };

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-muted/40 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}

export function ResultView({ result }: { result: ScanResult }) {
  const phishing = result.prediction === "phishing";
  const meta = SCAN_META[result.scan_type];
  const TypeIcon = meta.icon;
  const { explanation } = result;
  const maxWeight = Math.max(0.0001, ...explanation.top_terms.map((t) => Math.abs(t.weight)));

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,360px)_minmax(0,1fr)]">
      <div className="space-y-6">
        <Card className={cn("border-2", phishing ? "border-danger/40" : "border-safe/40")}>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              {phishing ? <AlertOctagon className="h-8 w-8 text-danger" /> : <CheckCircle2 className="h-8 w-8 text-safe" />}
              <div>
                <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  <TypeIcon className="h-3.5 w-3.5" /> {meta.label} classification
                </p>
                <p className={cn("text-2xl font-semibold", phishing ? "text-danger" : "text-safe")}>{phishing ? meta.threat : "Safe"}</p>
              </div>
            </div>
            <div className="mt-6">
              <RiskGauge score={result.risk_score} level={result.risk_level} />
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3">
              <Metric label="Risk score" value={formatPercent(result.risk_score)} />
              <Metric label="Confidence" value={formatPercent(result.confidence_score)} />
              <Metric label={`${meta.threat} probability`} value={result.probability.toFixed(4)} />
              <Metric label="Risk level" value={result.risk_level[0].toUpperCase() + result.risk_level.slice(1)} />
            </div>
            <p className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              Scanned {formatDateTime(result.created_at)}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-primary" /> Why this result
            </CardTitle>
            <CardDescription>{explanation.summary}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {explanation.factors.length === 0 && <p className="text-sm text-muted-foreground">No rule-based warning signs were found in the sender, links or wording.</p>}
            {explanation.factors.map((f) => (
              <div key={f.type} className={cn("rounded-md border p-4", SEVERITY_STYLE[f.severity])}>
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{f.title}</p>
                  <Badge variant={SEVERITY_BADGE[f.severity]} className="capitalize">
                    {f.severity}
                  </Badge>
                </div>
                <p className="mt-1.5 text-sm text-foreground/80">{f.detail}</p>
                {f.evidence.length > 0 && (
                  <ul className="mt-2 flex flex-wrap gap-1.5">
                    {f.evidence.map((e) => (
                      <li key={e} className="max-w-full truncate rounded bg-background/60 px-2 py-1 text-xs text-foreground/80" title={e}>
                        {e}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {explanation.top_terms.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{result.scan_type === "url" ? "Signals that influenced the model" : "Words that influenced the model"}</CardTitle>
              <CardDescription>Red items pushed the score toward {meta.threat.toLowerCase()}. Green items pushed it toward legitimate.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {explanation.top_terms.map((t) => (
                <div key={t.term} className="grid grid-cols-[110px_1fr] items-center gap-3 text-sm sm:grid-cols-[140px_1fr]">
                  <span className="truncate" title={t.term}>
                    {t.term}
                  </span>
                  <div className="h-2 rounded-full bg-muted">
                    <div className={cn("h-2 rounded-full", t.direction === "phishing" ? "bg-danger" : "bg-safe")} style={{ width: `${Math.max(4, (Math.abs(t.weight) / maxWeight) * 100)}%` }} />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TypeIcon className="h-4 w-4 text-primary" /> Analyzed {meta.noun}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {result.scan_type === "email" && (
              <>
                <div>
                  <p className="text-xs text-muted-foreground">Subject</p>
                  <p className="break-words">{result.subject || "(no subject)"}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Sender</p>
                  <p className="flex items-center gap-1.5 break-all">
                    <Link2 className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                    {result.sender}
                  </p>
                </div>
              </>
            )}
            {result.scan_type === "sms" && (
              <div>
                <p className="text-xs text-muted-foreground">Sender</p>
                <p className="break-all">{result.sender || "(not provided)"}</p>
              </div>
            )}
            <div>
              <p className="text-xs text-muted-foreground">{result.scan_type === "email" ? "Body" : result.scan_type === "url" ? "URL" : "Message"}</p>
              <pre className="mt-1 max-h-72 overflow-auto whitespace-pre-wrap break-all rounded-md border bg-muted/40 p-3 font-sans text-sm text-foreground/90">{result.body}</pre>
            </div>
            {result.scan_type === "url" && <p className="text-xs text-muted-foreground">ThreatGuard analyzed the text of this address only. It was never opened.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
