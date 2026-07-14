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

  return (
    <article className="group flex flex-col overflow-hidden rounded-lg border bg-card transition-colors hover:border-muted-foreground/30">
      <ProductImage src={productImage(product)} alt={product.name} />

      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-baseline justify-between gap-3">
          <h3 className="text-base font-semibold leading-snug">
            {product.name}
          </h3>
          {(product.portion || product.weight) && (
            <span className="shrink-0 text-xs text-muted-foreground">
              {product.portion ?? formatWeight(product.weight!)}
            </span>
          )}
        </div>

        <p className="line-clamp-3 flex-1 text-sm leading-relaxed text-muted-foreground">
          {product.description}
        </p>

        <div className="mt-2 flex items-center justify-between gap-3">
          <span className="text-lg font-bold tabular-nums">
            {formatPrice(product.price)}
          </span>

          <div className="w-32">
            {quantity === 0 ? (
              <Button
                className="w-full animate-fade-in"
                onClick={() => addItem(product)}
              >
                <Plus />
                В корзину
              </Button>
            ) : (
              <QuantityControl
                className="w-full animate-fade-in"
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
