"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { SCAN_META } from "@/lib/scan-types";
import type { ScanType } from "@/types";

type Severity = "high" | "medium";
interface Finding {
  id: string;
  severity: Severity;
  title: string;
  detail: string;
}
interface Segment {
  text: string;
  finding?: string;
}
interface Sample {
  meta: { label: string; value: Segment[] }[];
  body: Segment[];
  verdict: string;
  risk: number;
  findings: Finding[];
}

const SAMPLES: Record<ScanType, Sample> = {
  email: {
    meta: [
      { label: "From", value: [{ text: "PayPal Support <" }, { text: "paypal-support@paypa1-secure.xyz", finding: "sender" }, { text: ">" }] },
      { label: "Subject", value: [{ text: "Action required: your account will be suspended" }] },
    ],
    body: [
      { text: "We noticed unusual activity on your account. " },
      { text: "Verify your account within 24 hours", finding: "urgency" },
      { text: " or access will be limited. Sign in here: " },
      { text: "http://192.168.4.5/paypal/login", finding: "link" },
    ],
    verdict: "Phishing",
    risk: 96,
    findings: [
      { id: "sender", severity: "high", title: "Sender is not PayPal", detail: "The domain paypa1-secure.xyz is not paypal.com, and .xyz is a high-abuse extension." },
      { id: "urgency", severity: "medium", title: "Deadline pressure", detail: "A 24-hour limit leaves no time to check whether the message is real." },
      { id: "link", severity: "high", title: "Link goes to a bare IP address", detail: "Real services link to their own domain, over https." },
    ],
  },
  url: {
    meta: [],
    body: [
      { text: "http://", finding: "scheme" },
      { text: "paypal-secure-login.xyz", finding: "host" },
      { text: "/verify/account", finding: "path" },
      { text: "?id=4417" },
    ],
    verdict: "Malicious",
    risk: 97,
    findings: [
      { id: "host", severity: "high", title: "Brand name on an unrelated domain", detail: "paypal appears in the host, but the registered domain is paypal-secure-login.xyz." },
      { id: "path", severity: "medium", title: "Login and verify keywords", detail: "Words like verify and account are typical of fake sign-in pages." },
      { id: "scheme", severity: "medium", title: "Not encrypted", detail: "The link uses http instead of https." },
    ],
  },
  sms: {
    meta: [{ label: "From", value: [{ text: "+91 90000 12345" }] }],
    body: [
      { text: "Your KYC has expired. " },
      { text: "Update within 24 hours", finding: "urgency" },
      { text: " or your account will be blocked: " },
      { text: "bit.ly/3xKyc99", finding: "link" },
      { text: " Questions? Reply with your " },
      { text: "OTP", finding: "otp" },
    ],
    verdict: "Scam",
    risk: 91,
    findings: [
      { id: "otp", severity: "high", title: "Asks for a one-time code", detail: "Banks never ask you to text back an OTP." },
      { id: "link", severity: "high", title: "Shortened link", detail: "The real destination is hidden behind bit.ly." },
      { id: "urgency", severity: "medium", title: "Account-block threat", detail: "A deadline plus a penalty is the standard scam pressure pattern." },
    ],
  },
};

const MARK: Record<Severity, { idle: string; active: string; dot: string }> = {
  high: { idle: "bg-danger/15 decoration-danger/70", active: "bg-danger/40 decoration-danger", dot: "bg-danger" },
  medium: { idle: "bg-warn/15 decoration-warn/70", active: "bg-warn/40 decoration-warn", dot: "bg-warn" },
};

export function HeroDemo() {
  const [type, setType] = useState<ScanType>("email");
  const [active, setActive] = useState<string | null>(null);
  const sample = SAMPLES[type];
  const severityOf = (id?: string) => sample.findings.find((f) => f.id === id)?.severity ?? "high";

  function renderSegments(segments: Segment[]) {
    return segments.map((seg, i) =>
      seg.finding ? (
        <mark
          key={i}
          className={cn(
            "rounded-sm px-0.5 text-foreground underline decoration-wavy underline-offset-4 transition-colors",
            active === seg.finding ? MARK[severityOf(seg.finding)].active : MARK[severityOf(seg.finding)].idle
          )}
        >
          {seg.text}
        </mark>
      ) : (
        <span key={i}>{seg.text}</span>
      )
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border bg-card/90 shadow-2xl shadow-black/40">
      <div role="tablist" aria-label="Sample threat type" className="flex border-b bg-muted/40">
        {(Object.keys(SAMPLES) as ScanType[]).map((t) => {
          const { label, icon: Icon } = SCAN_META[t];
          const selected = t === type;
          return (
            <button
              key={t}
              role="tab"
              aria-selected={selected}
              onClick={() => {
                setType(t);
                setActive(null);
              }}
              className={cn(
                "flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring",
                selected ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          );
        })}
      </div>

      <div className="space-y-4 p-5" role="tabpanel">
        <div className="rounded-lg border bg-background/60 p-4 text-sm leading-relaxed">
          {sample.meta.map((m) => (
            <p key={m.label} className="mb-1 break-words text-muted-foreground">
              <span className="mr-2 text-xs">{m.label}</span>
              <span className="text-foreground/90">{renderSegments(m.value)}</span>
            </p>
          ))}
          <p className={cn("break-words text-foreground/90", sample.meta.length > 0 && "mt-3", type === "url" && "text-base")}>{renderSegments(sample.body)}</p>
        </div>

        <div className="flex items-center gap-4">
          <div>
            <p className="text-xs text-muted-foreground">Verdict</p>
            <p className="text-lg font-semibold text-danger">{sample.verdict}</p>
          </div>
          <div className="flex-1">
            <div className="mb-1 flex justify-between text-xs text-muted-foreground">
              <span>Risk score</span>
              <span className="tabular-nums text-foreground">{sample.risk} / 100</span>
            </div>
            <div className="h-2 rounded-full bg-muted">
              <div className="h-2 rounded-full bg-danger transition-[width] duration-700" style={{ width: `${sample.risk}%` }} />
            </div>
          </div>
        </div>

        <ul className="space-y-1.5">
          {sample.findings.map((f) => (
            <li key={f.id}>
              <button
                type="button"
                onMouseEnter={() => setActive(f.id)}
                onMouseLeave={() => setActive(null)}
                onFocus={() => setActive(f.id)}
                onBlur={() => setActive(null)}
                className={cn(
                  "flex w-full items-start gap-3 rounded-md border px-3 py-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  active === f.id ? "border-primary/50 bg-primary/10" : "border-border bg-transparent"
                )}
              >
                <span className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", MARK[f.severity].dot)} />
                <span>
                  <span className="block text-sm font-medium">{f.title}</span>
                  <span className="block text-xs text-muted-foreground">{f.detail}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
        <p className="text-xs text-muted-foreground">Illustrative sample, not a live scan. Hover a finding to see where it comes from.</p>
      </div>
    </div>
  );
}
