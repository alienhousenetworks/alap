import type { Metadata } from "next";

export const metadata: Metadata = { title: "ALAP Operations", robots: { index: false, follow: false } };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body style={{margin:0,fontFamily:"Arial, sans-serif",background:"#0c0e12",color:"#f4f2ee"}}>{children}</body></html>;
}
