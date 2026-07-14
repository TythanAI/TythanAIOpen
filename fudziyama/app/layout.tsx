import type { Metadata, Viewport } from "next";
import { Manrope } from "next/font/google";

import { SITE } from "@/lib/site";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { CartSheet } from "@/components/cart-sheet";

import "./globals.css";

const manrope = Manrope({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
  title: `${SITE.name} — доставка суши, роллов и сетов в Усть-Куте`,
  description: `${SITE.name}: доставка японской кухни в Усть-Куте. ${SITE.deliveryNote}. Телефон: ${SITE.phone}. Адрес: ${SITE.address}.`,
};

export const viewport: Viewport = {
  themeColor: "#f6f6f8",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body className={manrope.className}>
        <SiteHeader />
        <main>{children}</main>
        <SiteFooter />
        <CartSheet />
      </body>
    </html>
  );
}
