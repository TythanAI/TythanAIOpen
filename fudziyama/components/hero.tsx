import { Clock, MapPin, Phone } from "lucide-react";

import { SITE } from "@/lib/site";

export function Hero() {
  return (
    <section className="container pt-5">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#e3342b] to-[#a31f18] px-6 py-10 text-white sm:px-12 sm:py-14">
        {/* Силуэт Фудзиямы */}
        <svg
          className="pointer-events-none absolute -right-8 bottom-0 h-full w-auto opacity-20 sm:opacity-30"
          viewBox="0 0 400 200"
          aria-hidden
        >
          <path
            d="M 0 200 L 120 60 Q 140 35 160 60 L 280 200 Z"
            fill="#ffffff"
          />
          <path
            d="M 120 60 Q 140 35 160 60 L 172 74 Q 160 88 150 74 Q 140 88 128 70 Z"
            fill="#7f1712"
          />
        </svg>

        <div className="relative max-w-xl">
          <h1 className="text-3xl font-extrabold leading-tight tracking-tight sm:text-5xl">
            Суши, роллы и сеты
            <br />с доставкой по Усть-Куту
          </h1>
          <p className="mt-3 text-sm text-white/85 sm:text-base">
            Готовим после заказа и привозим свежим. {SITE.deliveryNote}.
          </p>
          <a
            href={SITE.phoneHref}
            className="mt-6 inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-bold text-[#c22820] transition-transform hover:scale-[1.02]"
          >
            <Phone className="h-4 w-4" />
            {SITE.phone}
          </a>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-x-7 gap-y-2 px-1 text-sm text-muted-foreground lg:hidden">
        <span className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-primary" />
          {SITE.address}
        </span>
        <span className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-primary" />
          {SITE.workHours}
        </span>
        <span className="flex items-center gap-2">
          <Phone className="h-4 w-4 text-primary" />
          <a href={SITE.phoneHref} className="font-semibold text-foreground hover:text-primary">
            {SITE.phone}
          </a>
        </span>
      </div>
    </section>
  );
}
