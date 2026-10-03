"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SCAN_META, SCAN_TYPES } from "@/lib/scan-types";
import { cn } from "@/lib/utils";

export function AnalyzeTabs() {
  const pathname = usePathname();
  return (
    <nav aria-label="Content type" className="inline-flex rounded-lg border bg-muted/50 p-1">
      {SCAN_TYPES.map((type) => {
        const { label, href, icon: Icon } = SCAN_META[type];
        const active = pathname === href;
        return (
          <Link
            key={type}
            href={href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "inline-flex items-center gap-2 rounded-md px-3.5 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              active ? "bg-primary/20 text-primary" : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
