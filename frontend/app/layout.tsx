import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/lib/theme-context";
import { AuthProvider } from "@/lib/auth-context";
import { DocProvider } from "@/lib/doc-context";

export const metadata: Metadata = {
  title: "DocMind — Document Knowledge Assistant",
  description: "Ask your PDFs. Inspect the supporting pages.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased" suppressHydrationWarning>
      <body className="h-full flex flex-col font-sans overflow-hidden">
        <ThemeProvider>
          <AuthProvider>
            <DocProvider>{children}</DocProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
