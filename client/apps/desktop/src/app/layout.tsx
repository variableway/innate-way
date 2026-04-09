import type { Metadata } from "next";
import { AppShell } from "@/components/layout/app-shell";
import "@innate/ui/globals.css";

export const metadata: Metadata = {
  title: "Innate Capture",
  description: "Capture and organize your thoughts",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
