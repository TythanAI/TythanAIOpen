"use client";

import * as React from "react";
import Image from "next/image";

import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

interface ProductImageProps {
  src?: string;
  alt: string;
  className?: string;
  sizes?: string;
}

/**
 * Фото блюда с плавным появлением. Пока изображение грузится — показывается
 * skeleton-блок; если файла нет — фирменная заглушка вместо битой картинки.
 */
export function ProductImage({ src, alt, className, sizes }: ProductImageProps) {
  const [status, setStatus] = React.useState<"loading" | "loaded" | "error">(
    src ? "loading" : "error"
  );

  return (
    <div
      className={cn(
        "relative aspect-[4/3] w-full overflow-hidden bg-secondary",
        className
      )}
    >
      {status === "loading" && (
        <Skeleton className="absolute inset-0 rounded-none" />
      )}

      {src && status !== "error" && (
        <Image
          src={src}
          alt={alt}
          fill
          sizes={sizes ?? "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"}
          className={cn(
            "object-cover transition-all duration-500",
            status === "loaded" ? "opacity-100 blur-0" : "opacity-0 blur-md"
          )}
          onLoad={() => setStatus("loaded")}
          onError={() => setStatus("error")}
        />
      )}

      {status === "error" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-gradient-to-br from-secondary to-background">
          <span className="text-4xl" aria-hidden>
            🍣
          </span>
          <span className="text-xs text-muted-foreground">Фото скоро появится</span>
        </div>
      )}
    </div>
  );
}
