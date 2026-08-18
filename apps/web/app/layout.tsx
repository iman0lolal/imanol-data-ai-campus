import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Imanol Data & AI Campus",
  description: "Personal learning platform foundation"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
