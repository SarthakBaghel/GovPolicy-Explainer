"use client";

import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import { ArrowUp, Search, Sparkles } from "lucide-react";
import { ragApi, getErrorMessage } from "@/lib/api";
import type { DocumentItem, RagSearchItem } from "@/types";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Loader } from "@/components/ui/loader";
import { Textarea } from "@/components/ui/textarea";

interface DocumentInsightsPanelProps {
  document: DocumentItem;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  mode: "answer" | "search";
  content: string;
  sources: RagSearchItem[];
}

function createMessageId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function DocumentInsightsPanel({ document }: DocumentInsightsPanelProps) {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeAction, setActiveAction] = useState<"ask" | "search" | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);

  const docName = useMemo(() => `${document.user_id}/${document.doc_id}`, [document.doc_id, document.user_id]);
  const trimmedDraft = draft.trim();
  const hasMessages = messages.length > 0;

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, activeAction]);

  const onAsk = async (e?: FormEvent) => {
    e?.preventDefault();

    if (!trimmedDraft) {
      setError("Enter a question before asking this document.");
      return;
    }

    const prompt = trimmedDraft;
    setError(null);
    setActiveAction("ask");
    setMessages((current) => [
      ...current,
      {
        id: createMessageId(),
        role: "user",
        mode: "answer",
        content: prompt,
        sources: [],
      },
    ]);

    try {
      const [answerResponse, sourceResponse] = await Promise.all([
        ragApi.queryDocument(prompt, docName),
        ragApi.searchDocument(prompt, docName).catch(() => []),
      ]);

      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          mode: "answer",
          content: answerResponse.answer || "No answer was returned for this document.",
          sources: Array.isArray(sourceResponse) ? sourceResponse : [],
        },
      ]);
      setDraft("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setActiveAction(null);
    }
  };

  const onSearch = async () => {
    if (!trimmedDraft) {
      setError("Enter a phrase before searching the document.");
      return;
    }

    const prompt = trimmedDraft;
    setError(null);
    setActiveAction("search");
    setMessages((current) => [
      ...current,
      {
        id: createMessageId(),
        role: "user",
        mode: "search",
        content: prompt,
        sources: [],
      },
    ]);

    try {
      const response = await ragApi.searchDocument(prompt, docName);
      const results = Array.isArray(response) ? response : [];

      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          mode: "search",
          content: results.length
            ? "I found the most relevant passages for that request."
            : "I could not find a matching passage in this document.",
          sources: results,
        },
      ]);
      setDraft("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setActiveAction(null);
    }
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void onAsk();
    }
  };

  const renderComposer = (centered = false) => (
    <form className="w-full" onSubmit={onAsk}>
      <div className="rounded-[28px] border border-slate-200 bg-white px-4 py-4 shadow-[0_10px_30px_rgba(15,23,42,0.06)]">
        <Textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask anything about this document"
          className="min-h-[72px] resize-none border-0 bg-transparent px-0 py-0 text-base shadow-none focus-visible:ring-0"
          disabled={activeAction !== null}
        />

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-muted">
            {centered ? "Responses stay grounded in this uploaded document." : "Press Enter to send. Use Shift+Enter for a new line."}
          </p>

          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="outline" size="sm" disabled={activeAction !== null} onClick={onSearch}>
              {activeAction === "search" ? <Loader label="Searching" /> : <><Search size={14} className="mr-1.5" /> Find Exact Text</>}
            </Button>
            <Button type="submit" size="sm" disabled={activeAction !== null}>
              {activeAction === "ask" ? <Loader label="Asking" /> : <><ArrowUp size={14} className="mr-1.5" /> Ask</>}
            </Button>
          </div>
        </div>
      </div>
    </form>
  );

  return (
    <section className="overflow-hidden rounded-[30px] border border-slate-200 bg-[#fcfcfd] shadow-[0_18px_45px_rgba(15,23,42,0.06)]">
      {!hasMessages ? (
        <div className="flex min-h-[68vh] items-center justify-center px-6 py-12 sm:px-10">
          <div className="w-full max-w-3xl space-y-8">
            <div className="space-y-3 text-center">
              <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm text-slate-600">
                <Sparkles size={15} className="text-primary" />
                Ask questions about {document.filename}
              </div>
              <h2 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
                Ready when you are.
              </h2>
              <p className="mx-auto max-w-2xl text-sm leading-6 text-muted sm:text-base">
                Ask for summaries, eligibility rules, deadlines, benefits, or exact clauses from this one document.
              </p>
            </div>

            {error ? <Alert variant="error" message={error} /> : null}

            <div className="mx-auto w-full max-w-3xl">{renderComposer(true)}</div>
          </div>
        </div>
      ) : (
        <div className="flex min-h-[68vh] flex-col">
          <div className="flex-1 overflow-y-auto px-6 py-8 sm:px-10">
            <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
              {messages.map((message) => (
                <div key={message.id} className={message.role === "user" ? "ml-auto max-w-2xl" : "mr-auto max-w-2xl"}>
                  {message.role === "assistant" ? (
                    <div className="rounded-[28px] border border-slate-200 bg-white px-5 py-4 shadow-sm">
                      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                        {message.mode === "search" ? "Relevant Passages" : "Answer"}
                      </p>
                      <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{message.content}</p>

                      {message.sources.length > 0 ? (
                        <details className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-3">
                          <summary className="cursor-pointer list-none text-sm font-medium text-slate-700">
                            View supporting passages ({message.sources.length})
                          </summary>
                          <div className="mt-3 space-y-3">
                            {message.sources.map((source, index) => (
                              <div key={`${source.source}-${index}`} className="rounded-2xl border border-slate-200 bg-white p-3">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                  <p className="text-xs font-medium uppercase tracking-[0.14em] text-slate-500">{source.source}</p>
                                  <p className="text-xs text-muted">Score {source.score.toFixed(3)}</p>
                                </div>
                                <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{source.text}</p>
                              </div>
                            ))}
                          </div>
                        </details>
                      ) : null}
                    </div>
                  ) : (
                    <div className="rounded-[28px] bg-slate-900 px-5 py-4 text-sm leading-7 text-white shadow-sm">
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                  )}
                </div>
              ))}

              {activeAction ? (
                <div className="mr-auto max-w-2xl rounded-[28px] border border-slate-200 bg-white px-5 py-4 shadow-sm">
                  <Loader label={activeAction === "ask" ? "Reading the document" : "Scanning indexed passages"} />
                </div>
              ) : null}

              <div ref={endRef} />
            </div>
          </div>

          <div className="border-t border-slate-200 bg-[#fcfcfd] px-6 py-5 sm:px-10">
            <div className="mx-auto w-full max-w-3xl space-y-3">
              {error ? <Alert variant="error" message={error} /> : null}
              {renderComposer()}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
