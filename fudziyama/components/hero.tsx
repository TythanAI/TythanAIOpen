import { Clock, MapPin, Phone } from "lucide-react";

import { SITE } from "@/lib/site";

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,hsl(0_84%_55%/0.12),transparent_60%)]"
        aria-hidden
      />
      <div className="container relative flex flex-col items-start gap-6 py-16 sm:py-24">
        <p className="rounded-full bg-primary px-4 py-1.5 text-sm font-semibold text-primary-foreground">
          {SITE.tagline}
        </p>
        <h1 className="max-w-2xl text-4xl font-bold leading-tight tracking-tight sm:text-6xl">
          {SITE.name} — доставка японской кухни в Усть-Куте
        </h1>
        <p className="max-w-xl text-lg text-muted-foreground">
          Готовим из свежих продуктов и привозим горячим. {SITE.deliveryNote}.
        </p>

        <div className="flex flex-wrap gap-x-6 gap-y-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-2">
            <Phone className="h-4 w-4 text-primary" />
            <a href={SITE.phoneHref} className="font-medium text-foreground hover:text-primary">
              {SITE.phone}
            </a>
          </span>
          <span className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary" />
            {SITE.address}
          </span>
          <span className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            {SITE.workHours}
          </span>
        </div>
      </div>
    </section>
  );
}
