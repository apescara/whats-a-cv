import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "What's a CV?",
  description: "A local-first workspace for targeted job applications.",
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
