import type { Metadata, Viewport } from "next";
import { Sora } from "next/font/google";
import "./globals.css";

const sora = Sora({ subsets: ["latin"], variable: "--font-sora", display: "swap" });

export const metadata: Metadata = {
  title: { default: "ThreatGuard | AI-powered threat detection", template: "%s | ThreatGuard" },
  description: "Check emails, URLs and text messages for phishing, malicious links and scams. Get a risk score and a plain-language explanation.",
};

export const viewport: Viewport = { themeColor: "#05060d", colorScheme: "dark" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`dark ${sora.variable}`}>
      <body>{children}</body>
    </html>
  );
}
