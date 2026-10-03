import { Suspense } from "react";
import type { Metadata } from "next";
import { AuthForm } from "@/components/auth-form";
import { Logo } from "@/components/logo";

export const metadata: Metadata = { title: "Create account" };

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-5">
      <div className="w-full max-w-sm space-y-8">
        <div className="space-y-3 text-center">
          <div className="flex justify-center">
            <Logo />
          </div>
          <h1 className="text-2xl font-semibold">Create your account</h1>
        </div>
        <div className="rounded-xl border bg-card/80 p-6 backdrop-blur">
          <Suspense>
            <AuthForm mode="register" />
          </Suspense>
        </div>
      </div>
    </main>
  );
}
