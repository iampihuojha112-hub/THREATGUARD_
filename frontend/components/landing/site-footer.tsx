import Link from "next/link";
import { Logo } from "@/components/logo";

const COLUMNS = [
  {
    title: "Product",
    links: [
      { label: "Overview", href: "/#overview" },
      { label: "Detection", href: "/#detection" },
      { label: "How it works", href: "/#workflow" },
      { label: "Models", href: "/#models" },
      { label: "Dashboard", href: "/#dashboard" },
    ],
  },
  {
    title: "Analyze",
    links: [
      { label: "Email", href: "/analyze" },
      { label: "URL", href: "/analyze/url" },
      { label: "SMS", href: "/analyze/sms" },
    ],
  },
  {
    title: "Account",
    links: [
      { label: "Sign in", href: "/login" },
      { label: "Create account", href: "/register" },
      { label: "Scan history", href: "/history" },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t">
      <div className="mx-auto grid max-w-6xl gap-10 px-5 py-12 md:grid-cols-[1.4fr_repeat(3,1fr)]">
        <div className="max-w-xs">
          <Logo />
          <p className="mt-3 text-sm text-muted-foreground">Threat detection for the emails, links and text messages that reach you.</p>
        </div>
        {COLUMNS.map((col) => (
          <nav key={col.title} aria-label={col.title}>
            <p className="mb-3 text-sm font-medium">{col.title}</p>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {col.links.map((l) => (
                <li key={l.label}>
                  <Link href={l.href} className="transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        ))}
      </div>
      <div className="border-t">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-6 text-xs text-muted-foreground sm:flex-row sm:justify-between">
          <p>&copy; 2026 ThreatGuard</p>
          <p className="max-w-xl">ThreatGuard flags likely threats and is not a guarantee. If you are unsure about a message, contact the sender through a channel you already trust.</p>
        </div>
      </div>
    </footer>
  );
}
