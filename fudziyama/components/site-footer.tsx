import { Clock, MapPin, Phone } from "lucide-react";

import { SITE } from "@/lib/site";

export function SiteFooter() {
  return (
    <footer className="border-t py-10">
      <div className="container flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-1">
          <p className="text-lg font-bold">{SITE.name}</p>
          <p className="text-sm text-muted-foreground">{SITE.tagline}</p>
        </div>

        <div className="space-y-2 text-sm text-muted-foreground">
          <p className="flex items-center gap-2">
            <Phone className="h-4 w-4 text-primary" />
            <a href={SITE.phoneHref} className="text-foreground hover:text-primary">
              {SITE.phone}
            </a>
          </p>
          <p className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary" />
            {SITE.address}
          </p>
          <p className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            {SITE.workHours}
          </p>
        </div>
      </div>
      <div className="container mt-8 border-t pt-6">
        <p className="text-xs text-muted-foreground">
          © {new Date().getFullYear()} {SITE.name}. Доставка еды в г. Усть-Кут.
        </p>
      </div>
    </footer>
  );
}
