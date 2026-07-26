import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";

import { QueryProvider } from "@/providers/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "EcoPackAI | Enterprise Analytics",
  description: "AI-Powered Sustainable Packaging Recommendation System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen flex antialiased bg-background text-foreground selection:bg-primary/30`}>
        <QueryProvider>
          <Sidebar />
          <div className="flex-1 flex flex-col h-screen overflow-hidden">
            <Navbar />
            <main className="flex-1 overflow-y-auto bg-muted/20 p-8">
              <div className="max-w-7xl mx-auto space-y-8">
                {children}
              </div>
            </main>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
