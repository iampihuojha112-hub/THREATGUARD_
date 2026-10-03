import Link from "next/link";

export function Logo({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="inline-flex items-center gap-2.5 font-semibold tracking-tight">
      <svg width="28" height="28" viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <path d="M16 2.5 4.5 7v8.2c0 7.2 4.9 12.6 11.5 14.3 6.6-1.7 11.5-7.1 11.5-14.3V7L16 2.5Z" fill="hsl(262 83% 66% / 0.18)" stroke="hsl(262 83% 66%)" strokeWidth="1.6" />
        <path d="m11 16.2 3.6 3.6L21.5 12" stroke="hsl(262 83% 76%)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span className="text-lg">ThreatGuard</span>
    </Link>
  );
}
