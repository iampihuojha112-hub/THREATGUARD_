"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";

export function LogoutButton({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  async function logout() {
    setBusy(true);
    await createClient().auth.signOut();
    router.replace("/login");
    router.refresh();
  }

  return (
    <Button variant="ghost" size={compact ? "icon" : "default"} onClick={logout} disabled={busy} aria-label="Sign out" className={compact ? "" : "w-full justify-start"}>
      <LogOut className="h-4 w-4" />
      {!compact && <span>{busy ? "Signing out..." : "Sign out"}</span>}
    </Button>
  );
}
