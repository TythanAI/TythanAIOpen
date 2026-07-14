"use client";

import * as React from "react";
import { CheckCircle2, ShoppingBag, Trash2 } from "lucide-react";

import { productImage } from "@/lib/products";
import { SITE } from "@/lib/site";
import { formatPrice, formatWeight } from "@/lib/utils";
import { useCart, useCartTotalCount, useCartTotalPrice } from "@/store/use-cart";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { CheckoutForm } from "@/components/checkout-form";
import { ProductImage } from "@/components/product-image";
import { QuantityControl } from "@/components/quantity-control";

type CartStep = "cart" | "checkout" | "success";

export function CartSheet() {
  const isOpen = useCart((s) => s.isOpen);
  const setOpen = useCart((s) => s.setOpen);
  const items = useCart((s) => s.items);
  const increment = useCart((s) => s.increment);
  const decrement = useCart((s) => s.decrement);
  const removeItem = useCart((s) => s.removeItem);
  const totalCount = useCartTotalCount();
  const totalPrice = useCartTotalPrice();

  const [step, setStep] = React.useState<CartStep>("cart");
  const [orderId, setOrderId] = React.useState<string>("");

  const handleOpenChange = (open: boolean) => {
    setOpen(open);
    if (!open) {
      // Возвращаемся к списку при следующем открытии; экран успеха не сбрасываем
      // мгновенно, чтобы не было скачка во время анимации закрытия.
      setTimeout(() => setStep("cart"), 300);
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={handleOpenChange}>
      <SheetContent className="flex w-full flex-col p-0">
        <SheetHeader className="border-b px-6 py-4">
          <SheetTitle>
            {step === "checkout"
              ? "Оформление заказа"
              : step === "success"
                ? "Заказ принят"
                : "Корзина"}
          </SheetTitle>
          <SheetDescription className="sr-only">
            Панель корзины и оформления заказа
          </SheetDescription>
        </SheetHeader>

        {step === "success" ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
            <CheckCircle2 className="h-14 w-14 text-primary" />
            <div className="space-y-2">
              <p className="text-lg font-semibold">Спасибо за заказ!</p>
              <p className="text-sm text-muted-foreground">
                Номер заказа: <span className="font-mono text-foreground">{orderId}</span>
              </p>
              <p className="text-sm text-muted-foreground">
                Мы свяжемся с вами для подтверждения. Если возникнут вопросы —
                звоните: {SITE.phone}
              </p>
            </div>
            <Button onClick={() => handleOpenChange(false)}>Вернуться к меню</Button>
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
            <ShoppingBag className="h-12 w-12 text-muted-foreground" />
            <div className="space-y-1">
              <p className="font-semibold">Корзина пуста</p>
              <p className="text-sm text-muted-foreground">
                Добавьте что-нибудь вкусное из меню
              </p>
            </div>
            <Button variant="secondary" onClick={() => handleOpenChange(false)}>
              Перейти к меню
            </Button>
          </div>
        ) : step === "checkout" ? (
          <div className="flex-1 overflow-y-auto px-6 py-4">
            <CheckoutForm
              onBack={() => setStep("cart")}
              onSuccess={(id) => {
                setOrderId(id);
                setStep("success");
              }}
            />
          </div>
        ) : (
          <>
            <ul className="flex-1 divide-y overflow-y-auto px-6">
              {items.map(({ product, quantity }) => (
                <li key={product.id} className="flex gap-3 py-4">
                  <ProductImage
                    src={productImage(product)}
                    alt={product.name}
                    className="h-20 w-20 shrink-0 rounded-md aspect-square"
                    sizes="80px"
                  />
                  <div className="flex min-w-0 flex-1 flex-col justify-between">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">{product.name}</p>
                        {(product.portion || product.weight) && (
                          <p className="text-xs text-muted-foreground">
                            {product.portion ?? formatWeight(product.weight!)}
                          </p>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 shrink-0 text-muted-foreground hover:text-destructive"
                        onClick={() => removeItem(product.id)}
                        aria-label={`Убрать ${product.name} из корзины`}
                      >
                        <Trash2 />
                      </Button>
                    </div>
                    <div className="flex items-center justify-between gap-2">
                      <QuantityControl
                        size="sm"
                        className="w-24"
                        quantity={quantity}
                        onIncrement={() => increment(product.id)}
                        onDecrement={() => decrement(product.id)}
                      />
                      <span className="text-sm font-semibold tabular-nums">
                        {formatPrice(product.price * quantity)}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>

            <div className="space-y-3 border-t px-6 py-4">
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>Товаров</span>
                <span className="tabular-nums">{totalCount} шт.</span>
              </div>
              <div className="flex items-center justify-between text-lg font-bold">
                <span>Итого</span>
                <span className="tabular-nums">{formatPrice(totalPrice)}</span>
              </div>
              <Button size="lg" className="w-full" onClick={() => setStep("checkout")}>
                Оформить заказ
              </Button>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
