"use client";

import * as React from "react";
import { Phone, ShoppingBag } from "lucide-react";

import { SITE } from "@/lib/site";
import { formatPrice } from "@/lib/utils";
import { useCart, useCartTotalCount, useCartTotalPrice } from "@/store/use-cart";
import { Button } from "@/components/ui/button";

export function SiteHeader() {
  const openCart = useCart((s) => s.openCart);
  const totalCount = useCartTotalCount();
  const totalPrice = useCartTotalPrice();

  // Счётчик корзины появляется только после гидратации localStorage.
  const [hydrated, setHydrated] = React.useState(false);
  React.useEffect(() => setHydrated(true), []);
  const count = hydrated ? totalCount : 0;

  return (
    <header className="sticky top-0 z-50 h-16 border-b bg-background/90 backdrop-blur-md">
      <div className="container flex h-full items-center justify-between gap-4">
        <a href="#" className="flex items-baseline gap-2">
          <span className="text-xl font-bold tracking-tight">{SITE.name}</span>
          <span className="hidden text-xs text-muted-foreground sm:inline">
            {SITE.tagline}
          </span>
        </a>

        <div className="flex items-center gap-2">
          <a
            href={SITE.phoneHref}
            className="hidden items-center gap-2 text-sm font-medium transition-colors hover:text-primary md:flex"
          >
            <Phone className="h-4 w-4" />
            {SITE.phone}
          </a>

          <Button onClick={openCart} className="relative" aria-label="Открыть корзину">
            <ShoppingBag />
            <span className="hidden sm:inline">
              {count > 0 ? formatPrice(totalPrice) : "Корзина"}
            </span>
            {count > 0 && (
              <span className="absolute -right-2 -top-2 flex h-5 min-w-5 items-center justify-center rounded-full bg-foreground px-1 text-xs font-bold text-background">
                {count}
              </span>
            )}
          </Button>
        </div>
      </div>
    </header>
  );
}
