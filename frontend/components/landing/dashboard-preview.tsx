/** Static illustration of the dashboard using sample numbers. Drawn with SVG so it needs no client code. */
const THREATS = [12, 18, 15, 22, 19, 27, 24, 31];
const SAFE = [40, 46, 52, 49, 58, 61, 66, 72];
const RECENT = [
  { type: "URL", title: "http://paypal-secure-login.xyz/verify", verdict: "Malicious", bad: true, risk: 97 },
  { type: "SMS", title: "Your parcel could not be delivered. Pay a fee at...", verdict: "Scam", bad: true, risk: 88 },
  { type: "Email", title: "Q3 roadmap - notes from today's meeting", verdict: "Safe", bad: false, risk: 6 },
  { type: "URL", title: "https://docs.python.org/3/library/json.html", verdict: "Safe", bad: false, risk: 3 },
];
const STATS = [
  ["Email scans", "128"],
  ["URL scans", "342"],
  ["SMS scans", "96"],
  ["Threats detected", "211"],
  ["Safe content", "355"],
  ["Average risk", "31.4%"],
];

export function DashboardPreview() {
  const max = Math.max(...THREATS.map((t, i) => t + SAFE[i]));
  const w = 520;
  const h = 170;
  const slot = w / THREATS.length;
  const barW = slot * 0.56;

  return (
    <div className="overflow-hidden rounded-xl border bg-card/90 shadow-2xl shadow-black/40" aria-label="Dashboard preview with sample data">
      <div className="flex items-center gap-1.5 border-b bg-muted/40 px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-border" />
        <span className="h-2.5 w-2.5 rounded-full bg-border" />
        <span className="h-2.5 w-2.5 rounded-full bg-border" />
        <span className="ml-3 text-xs text-muted-foreground">Dashboard (sample data)</span>
      </div>
      <div className="grid gap-px bg-border sm:grid-cols-3 lg:grid-cols-6">
        {STATS.map(([label, value]) => (
          <div key={label} className="bg-card px-4 py-3">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="text-xl font-semibold tabular-nums">{value}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-6 p-5 lg:grid-cols-[1.3fr_1fr]">
        <div>
          <p className="mb-3 text-sm font-medium">Weekly trend</p>
          <svg viewBox={`0 0 ${w} ${h + 22}`} className="w-full" role="img" aria-label="Stacked bars of threats and safe scans per week over eight weeks, rising from 52 to 103">
            {[0.25, 0.5, 0.75, 1].map((g) => (
              <line key={g} x1="0" x2={w} y1={h - h * g} y2={h - h * g} stroke="hsl(228 35% 16%)" strokeDasharray="3 4" />
            ))}
            {THREATS.map((t, i) => {
              const x = i * slot + (slot - barW) / 2;
              const safeH = (SAFE[i] / max) * h;
              const threatH = (t / max) * h;
              return (
                <g key={i}>
                  <rect x={x} y={h - safeH} width={barW} height={safeH} rx="3" fill="#10b981" opacity="0.85" />
                  <rect x={x} y={h - safeH - threatH} width={barW} height={threatH} rx="3" fill="#f43f5e" />
                  <text x={x + barW / 2} y={h + 16} textAnchor="middle" fontSize="10" fill="#8b93b8">
                    W{i + 1}
                  </text>
                </g>
              );
            })}
          </svg>
          <p className="mt-1 flex gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-danger" /> Threats</span>
            <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-safe" /> Safe</span>
          </p>
        </div>
        <div>
          <p className="mb-3 text-sm font-medium">Recent activity</p>
          <ul className="divide-y">
            {RECENT.map((r) => (
              <li key={r.title} className="flex items-center gap-3 py-2.5">
                <span className="w-9 shrink-0 text-xs text-muted-foreground">{r.type}</span>
                <span className="min-w-0 flex-1 truncate text-sm">{r.title}</span>
                <span className="text-xs tabular-nums text-muted-foreground">{r.risk}%</span>
                <span className={r.bad ? "w-[4.5rem] text-right text-xs font-medium text-danger" : "w-[4.5rem] text-right text-xs font-medium text-safe"}>{r.verdict}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
