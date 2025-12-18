"use client"; // This is necessary for using hooks in a Next.js app/layout.tsx

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { useState, useEffect } from 'react';
import { SocketProvider } from '../../the-ai-helping-tool/contexts/SocketContext'; // Adjust path as needed

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "The AI Helping Tool",
  description: "An AI-powered tool to help you learn and study more effectively.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [token, setToken] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // In a real application, you would fetch the token from local storage,
    // a cookie, or an authentication context.
    // For demonstration, we'll use a dummy token.
    // Ensure this token is valid for your backend's JWT secret key.
    // Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.Pz13-hE2o27zWlD201b1Q3o43-F4f4e4f4f4f4f4f4f
    // (This token assumes user ID '1' and a SECRET_KEY='your-secret-key' with ALGORITHM='HS256')
    const dummyToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.Pz13-hE2o27zWlD201b1Q3o43-F4f4f4f4f4f4f4f4f";
    setToken(dummyToken);
  }, []);

  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        {isClient && token ? ( // Only render SocketProvider on client-side and when token is available
          <SocketProvider token={token}>
            {children}
          </SocketProvider>
        ) : (
          children // Render children directly if not client-side or token not ready
        )}
      </body>
    </html>
  );
}