"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthForm } from "@/components/auth/auth-form";
import { getToken } from "@/lib/auth";

export default function AuthPage() {
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    if (token) {
      router.replace("/dashboard");
    }
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4 sm:p-6">
      <div className="grid w-full max-w-5xl gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="hidden rounded-xl border border-border bg-white p-8 lg:block">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Government Policy Explainer</p>
          <h1 className="mt-3 text-3xl font-semibold leading-tight text-foreground">
            Explain policy documents with clarity and confidence.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-muted">
            A focused workspace for uploading policy PDFs, tracking indexed records, and managing documents through a secure, readable dashboard.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-4 text-sm">
            <div className="rounded-lg border border-border bg-slate-50 p-4">
              <p className="font-medium text-slate-800">Secure Access</p>
              <p className="mt-1 text-muted">JWT-based auth for protected routes.</p>
            </div>
            <div className="rounded-lg border border-border bg-slate-50 p-4">
              <p className="font-medium text-slate-800">Readable Layout</p>
              <p className="mt-1 text-muted">Minimal, dashboard-first interface.</p>
            </div>
          </div>
        </section>
        <section className="flex items-center justify-center">
          <AuthForm />
        </section>
      </div>
    </div>
  );
}
