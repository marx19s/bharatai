import type { Metadata, Viewport } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const outfit = Outfit({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "BharatAI - Sovereign AI Assistant",
  description: "Next-generation multilingual AI workspace with Chat, Web Search, PDF extraction, Voice, Translation, and Grammar correction.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover"
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${outfit.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#0b0c16] text-[#eef2ff] overflow-hidden relative">
        {/* Glow ambient blobs */}
        <div className="absolute top-0 right-0 w-[45vw] h-[45vh] rounded-full bg-purple-500/10 blur-[130px] pointer-events-none animate-blob-1 z-0" />
        <div className="absolute bottom-[10%] left-[5%] w-[40vw] h-[40vh] rounded-full bg-blue-500/10 blur-[140px] pointer-events-none animate-blob-2 z-0" />
        <div className="absolute top-[40%] left-[30%] w-[35vw] h-[35vh] rounded-full bg-pink-500/5 blur-[120px] pointer-events-none animate-blob-3 z-0" />
        <div className="relative z-10 flex flex-col h-full w-full">
          {children}
        </div>
      </body>
    </html>
  );
}
