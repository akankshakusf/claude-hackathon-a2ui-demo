import type { Metadata } from "next";
import "./globals.css";
import "./a2ui-theme.css";

export const metadata: Metadata = {
  title: "Morphic UI — Agent-Driven Generative Interfaces",
  description:
    "Describe any interface. Claude reasons about your intent and assembles a live, interactive UI using A2A protocol and A2UI declarative JSON.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        {/* Google Fonts for A2UI Lit web components */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Google+Sans+Code&family=Google+Sans+Flex:opsz,wght,ROND@6..144,1..1000,100&family=Google+Sans:opsz,wght@17..18,400..700&display=block&family=IBM+Plex+Serif:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&display=swap"
        />
        {/* Material Symbols for A2UI icons */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
