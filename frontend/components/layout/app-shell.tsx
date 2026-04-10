"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { FileText, LayoutDashboard, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { clearToken } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();

  const onLogout = () => {
    clearToken();
    router.replace("/auth");
  };

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  ];

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-30 border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
          <p className="text-sm font-medium text-foreground">GovPolicy Explainer</p>
          <Button variant="outline" size="sm" onClick={onLogout}>
            <LogOut size={14} className="mr-1" /> Logout
          </Button>
        </div>
      </header>

      <div className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-6 px-4 py-6 sm:px-6 md:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="rounded-xl border border-border bg-[#f2f2f3] p-3">
          <nav className="space-y-1">
            {links.map((item) => {
              const Icon = item.icon;
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition",
                    active ? "bg-white text-foreground" : "text-slate-600 hover:bg-white/80"
                  )}
                >
                  <Icon size={16} />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-6 rounded-lg border border-border bg-white p-3 text-xs text-muted">
            <div className="mb-1 flex items-center gap-1.5 text-slate-700">
              <FileText size={14} />
              Document-first workflow
            </div>
            Upload policy PDFs, track metadata, and manage indexed records.
          </div>
        </aside>

        <main>{children}</main>
      </div>
    </div>
  );
}
