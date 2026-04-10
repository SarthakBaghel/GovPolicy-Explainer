"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Trash2 } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader } from "@/components/ui/loader";
import { ConfirmModal } from "@/components/ui/modal";
import { documentApi, getErrorMessage } from "@/lib/api";
import { getToken } from "@/lib/auth";
import type { DocumentItem } from "@/types";

export default function DocumentDetailPage() {
  const params = useParams<{ docId: string }>();
  const docId = params.docId;
  const router = useRouter();

  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/auth");
      return;
    }

    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await documentApi.getById(docId);
        setDocument(result);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    run();
  }, [docId, router]);

  const onDelete = async () => {
    setDeleteLoading(true);
    try {
      await documentApi.remove(docId);
      router.replace("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setDeleteLoading(false);
      setDeleteOpen(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Document Details</h1>
            <p className="mt-1 text-sm text-muted">Inspect metadata and manage this uploaded file.</p>
          </div>
          <Link href="/dashboard">
            <Button variant="outline">
              <ArrowLeft size={14} className="mr-1" /> Back to Dashboard
            </Button>
          </Link>
        </div>

        {error ? <Alert variant="error" message={error} /> : null}

        {loading ? (
          <Card>
            <CardContent className="pt-6">
              <Loader label="Loading document" />
            </CardContent>
          </Card>
        ) : !document ? (
          <Card>
            <CardContent className="pt-6">
              <div className="rounded-lg border border-dashed border-border bg-slate-50 p-6 text-center">
                <p className="text-sm font-medium text-slate-700">No search results for this document</p>
                <p className="mt-1 text-sm text-muted">The document may have been deleted or is unavailable.</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>{document.filename}</CardTitle>
              <CardDescription>Document ID: {document.doc_id}</CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="grid gap-4 text-sm sm:grid-cols-2">
                <div className="rounded-lg border border-border bg-slate-50 p-4">
                  <dt className="text-xs uppercase tracking-wide text-muted">Status</dt>
                  <dd className="mt-2"><Badge label={document.status || "indexed"} intent="success" /></dd>
                </div>
                <div className="rounded-lg border border-border bg-slate-50 p-4">
                  <dt className="text-xs uppercase tracking-wide text-muted">Uploaded At</dt>
                  <dd className="mt-2 font-medium text-slate-700">{new Date(document.created_at).toLocaleString()}</dd>
                </div>
                <div className="rounded-lg border border-border bg-slate-50 p-4">
                  <dt className="text-xs uppercase tracking-wide text-muted">File Size</dt>
                  <dd className="mt-2 font-medium text-slate-700">{(document.file_size / 1024).toFixed(1)} KB</dd>
                </div>
                <div className="rounded-lg border border-border bg-slate-50 p-4">
                  <dt className="text-xs uppercase tracking-wide text-muted">Owner</dt>
                  <dd className="mt-2 font-medium text-slate-700">{document.user_id}</dd>
                </div>
              </dl>

              <div className="mt-6">
                <Button variant="danger" onClick={() => setDeleteOpen(true)}>
                  <Trash2 size={14} className="mr-1" /> Delete Document
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <ConfirmModal
        open={deleteOpen}
        title="Delete document"
        description="This will permanently remove the document and all processed index files."
        confirmLabel="Delete"
        loading={deleteLoading}
        onConfirm={onDelete}
        onCancel={() => setDeleteOpen(false)}
      />
    </AppShell>
  );
}
