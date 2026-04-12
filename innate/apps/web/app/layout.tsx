import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Innate — Personal AI Assistant",
  description:
    "Ideas, Tasks, Agents — all in one workspace. For individuals and small teams.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
