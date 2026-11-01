import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ALAP — Meet your next favourite AI character",
  description: "Discover original AI characters, build your own universe and enjoy personalized interactive stories.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
