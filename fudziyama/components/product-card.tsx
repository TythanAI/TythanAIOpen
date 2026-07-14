"use client";

import * as React from "react";
import { Plus } from "lucide-react";

import { productImage, type Product } from "@/lib/products";
import { formatPrice, formatWeight } from "@/lib/utils";
import { useCart, useCartItem } from "@/store/use-cart";
import { Button } from "@/components/ui/button";
import { ProductImage } from "@/components/product-image";
import { QuantityControl } from "@/components/quantity-control";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const cartItem = useCartItem(product.id);
  const addItem = useCart((s) => s.addItem);
  const increment = useCart((s) => s.increment);
  const decrement = useCart((s) => s.decrement);

  // До гидратации localStorage-корзины рендерим кнопку «В корзину»,
  // чтобы серверная и клиентская разметка совпадали.
  const [hydrated, setHydrated] = React.useState(false);
  React.useEffect(() => setHydrated(true), []);
  const quantity = hydrated ? cartItem?.quantity ?? 0 : 0;

  const measure = product.portion ?? (product.weight ? formatWeight(product.weight) : null);

  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl bg-card shadow-sm ring-1 ring-black/5 transition-shadow hover:shadow-lg">
      <div className="relative">
        <ProductImage src={productImage(product)} alt={product.name} />
        {measure && (
          <span className="absolute right-3 top-3 rounded-full bg-card/90 px-2.5 py-1 text-xs font-semibold text-muted-foreground shadow-sm backdrop-blur">
            {measure}
          </span>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-1.5 p-4">
        <h3 className="text-base font-bold leading-snug">{product.name}</h3>

        <p className="line-clamp-3 flex-1 text-[13px] leading-relaxed text-muted-foreground">
          {product.description}
        </p>

        <div className="mt-3 flex items-center justify-between gap-3">
          <span className="text-lg font-extrabold tabular-nums">
            {formatPrice(product.price)}
          </span>

          <div className="w-32">
            {quantity === 0 ? (
              <Button
                className="w-full animate-fade-in rounded-full font-bold"
                onClick={() => addItem(product)}
              >
                <Plus />
                В корзину
              </Button>
            ) : (
              <QuantityControl
                className="w-full animate-fade-in rounded-full"
                quantity={quantity}
                onIncrement={() => increment(product.id)}
                onDecrement={() => decrement(product.id)}
              />
            )}
          </div>
        </div>
      </div>
    </article>
  );
}
