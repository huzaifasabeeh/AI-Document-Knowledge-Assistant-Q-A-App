import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/lib/theme-context";
import { AuthProvider } from "@/lib/auth-context";
import { DocProvider } from "@/lib/doc-context";

export const metadata: Metadata = {
  title: "DocuMind - AI Document Knowledge Assistant",
  description: "Your documents. A little more intelligent. Grounded in your knowledge. Backed by sources.",
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
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
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
