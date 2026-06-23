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
      <head>
        <title>BharatAI - Sovereign AI Assistant</title>
        <meta name="description" content="Next-generation multilingual AI workspace with Chat, Web Search, PDF extraction, Voice, Translation, and Grammar correction." />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
      </head>
      <body className="min-h-full flex flex-col bg-[#0b0c16] text-[#eef2ff] overflow-hidden relative">
        <div className="relative z-10 flex flex-col h-full w-full bg-[#06070d]">
          {children}
        </div>
      </body>
    </html>
  );
}
