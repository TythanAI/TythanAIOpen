"use client";

import * as React from "react";
import { Clock, MapPin, Phone, ShoppingBag } from "lucide-react";

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
    <header className="sticky top-0 z-50 h-16 border-b bg-card/95 backdrop-blur-md">
      <div className="container flex h-full items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <a href="#" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-lg font-extrabold text-primary-foreground">
              Ф
            </span>
            <span className="text-lg font-extrabold tracking-tight">
              {SITE.name}
            </span>
          </a>
          <div className="hidden flex-col text-xs text-muted-foreground lg:flex">
            <span className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5" />
              {SITE.address}
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              {SITE.workHours}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={SITE.phoneHref}
            className="hidden items-center gap-2 text-sm font-bold transition-colors hover:text-primary md:flex"
          >
            <Phone className="h-4 w-4 text-primary" />
            {SITE.phone}
          </a>

          <Button
            onClick={openCart}
            className="relative rounded-full font-bold"
            aria-label="Открыть корзину"
          >
            <ShoppingBag />
            <span className="hidden sm:inline">
              {count > 0 ? formatPrice(totalPrice) : "Корзина"}
            </span>
            {count > 0 && (
              <span className="absolute -right-1.5 -top-1.5 flex h-5 min-w-5 items-center justify-center rounded-full border-2 border-card bg-foreground px-1 text-[11px] font-bold text-card">
                {count}
              </span>
            )}
          </Button>
        </div>
      </div>
    </header>
  );
}
