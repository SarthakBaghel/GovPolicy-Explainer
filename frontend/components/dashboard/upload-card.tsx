"use client";

import { FormEvent, useState } from "react";
import { UploadCloud } from "lucide-react";
import { documentApi, getErrorMessage } from "@/lib/api";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Loader } from "@/components/ui/loader";

interface UploadCardProps {
  onUploaded: () => Promise<void> | void;
}

export function UploadCard({ onUploaded }: UploadCardProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!file) {
      setError("Please select a PDF file to upload.");
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported.");
      return;
    }

    setLoading(true);
    try {
      const result = await documentApi.upload(file);
      setSuccess(`Uploaded ${result.filename} successfully.`);
      setFile(null);
      await onUploaded();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UploadCloud size={18} /> Upload Policy PDF
        </CardTitle>
        <CardDescription>Upload a new policy file for indexing and management.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-4">
          <Input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="file:mr-3 file:rounded-md file:border-0 file:bg-primary-soft file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-primary"
          />
          {error ? <Alert variant="error" message={error} /> : null}
          {success ? <Alert variant="success" message={success} /> : null}
          <Button type="submit" disabled={loading}>
            {loading ? <Loader label="Uploading" /> : "Upload PDF"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
