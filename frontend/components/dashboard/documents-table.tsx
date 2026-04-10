"use client";

import Link from "next/link";
import { useState } from "react";
import { Eye, Trash2 } from "lucide-react";
import { documentApi, getErrorMessage } from "@/lib/api";
import type { DocumentItem } from "@/types";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfirmModal } from "@/components/ui/modal";
import { Loader } from "@/components/ui/loader";

interface DocumentsTableProps {
  documents: DocumentItem[];
  loading: boolean;
  error: string | null;
  onRefresh: () => Promise<void> | void;
}

export function DocumentsTable({ documents, loading, error, onRefresh }: DocumentsTableProps) {
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const selectedDoc = documents.find((doc) => doc.doc_id === deleteId);

  const onDelete = async () => {
    if (!deleteId) {
      return;
    }

    setDeleteLoading(true);
    setActionError(null);
    try {
      await documentApi.remove(deleteId);
      setDeleteId(null);
      await onRefresh();
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Uploaded Documents</CardTitle>
        <CardDescription>Review indexed policy files and manage records.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {error ? <Alert variant="error" message={error} /> : null}
        {actionError ? <Alert variant="error" message={actionError} /> : null}

        {loading ? (
          <Loader label="Loading documents" />
        ) : documents.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border bg-slate-50 p-8 text-center">
            <p className="text-sm font-medium text-slate-700">No documents uploaded yet</p>
            <p className="mt-1 text-sm text-muted">Upload your first policy PDF to get started.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-3 py-2">Title</th>
                  <th className="px-3 py-2">Uploaded</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Size</th>
                  <th className="px-3 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.doc_id} className="border-b border-slate-100">
                    <td className="px-3 py-3 font-medium text-slate-800">{doc.filename}</td>
                    <td className="px-3 py-3 text-muted">{new Date(doc.created_at).toLocaleString()}</td>
                    <td className="px-3 py-3">
                      <Badge label={doc.status || "indexed"} intent="success" />
                    </td>
                    <td className="px-3 py-3 text-muted">{(doc.file_size / 1024).toFixed(1)} KB</td>
                    <td className="px-3 py-3">
                      <div className="flex items-center gap-2">
                        <Link href={'/documents/' + doc.doc_id}>
                          <Button variant="outline" size="sm">
                            <Eye size={14} className="mr-1" /> View
                          </Button>
                        </Link>
                        <Button variant="danger" size="sm" onClick={() => setDeleteId(doc.doc_id)}>
                          <Trash2 size={14} className="mr-1" /> Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <ConfirmModal
          open={Boolean(deleteId)}
          title="Delete document"
          description={
            selectedDoc
              ? `This will permanently remove ${selectedDoc.filename} and its indexed data.`
              : "This will permanently remove this document and its indexed data."
          }
          confirmLabel="Delete"
          loading={deleteLoading}
          onConfirm={onDelete}
          onCancel={() => setDeleteId(null)}
          footerNote="This action cannot be undone."
        />
      </CardContent>
    </Card>
  );
}
