import type { Metadata } from "next";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "GovPolicy Explainer",
  description: "Government Policy Explainer dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
