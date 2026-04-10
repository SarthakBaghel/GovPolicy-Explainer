"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { DocumentsTable } from "@/components/dashboard/documents-table";
import { UploadCard } from "@/components/dashboard/upload-card";
import { AppShell } from "@/components/layout/app-shell";
import { useDocuments } from "@/hooks/use-documents";
import { getToken } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const { documents, loading, error, refresh } = useDocuments();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/auth");
    }
  }, [router]);

  return (
    <AppShell>
      <div className="space-y-6">
        <section>
          <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
          <p className="mt-1 text-sm text-muted">Upload and manage policy documents from a single workspace.</p>
        </section>

        <UploadCard onUploaded={refresh} />

        <DocumentsTable
          documents={documents}
          loading={loading}
          error={error}
          onRefresh={refresh}
        />
      </div>
    </AppShell>
  );
}
