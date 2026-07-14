"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";

import { SITE } from "@/lib/site";
import { formatPrice, isValidRussianPhone } from "@/lib/utils";
import { useCart, useCartTotalPrice } from "@/store/use-cart";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

export type PaymentMethod = "cash" | "card";

interface CheckoutFormProps {
  onSuccess: (orderId: string) => void;
  onBack: () => void;
}

interface FieldErrors {
  name?: string;
  phone?: string;
  address?: string;
}

export function CheckoutForm({ onSuccess, onBack }: CheckoutFormProps) {
  const items = useCart((s) => s.items);
  const clear = useCart((s) => s.clear);
  const totalPrice = useCartTotalPrice();

  const [name, setName] = React.useState("");
  const [phone, setPhone] = React.useState("");
  const [address, setAddress] = React.useState("");
  const [payment, setPayment] = React.useState<PaymentMethod>("cash");
  const [comment, setComment] = React.useState("");
  const [errors, setErrors] = React.useState<FieldErrors>({});
  const [submitting, setSubmitting] = React.useState(false);
  const [submitError, setSubmitError] = React.useState<string | null>(null);

  const validate = (): boolean => {
    const next: FieldErrors = {};
    if (name.trim().length < 2) next.name = "Укажите имя";
    if (!isValidRussianPhone(phone)) next.phone = "Укажите корректный номер телефона";
    if (address.trim().length < 5) next.address = "Укажите адрес доставки";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validate() || submitting) return;

    setSubmitting(true);
    try {
      const response = await fetch("/api/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer: {
            name: name.trim(),
            phone: phone.trim(),
            address: address.trim(),
            payment,
            comment: comment.trim(),
          },
          items: items.map((i) => ({
            id: i.product.id,
            name: i.product.name,
            price: i.product.price,
            quantity: i.quantity,
          })),
          total: totalPrice,
        }),
      });

      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error ?? "Не удалось оформить заказ");
      }

      clear();
      onSuccess(data.orderId);
    } catch {
      setSubmitError(
        `Не удалось отправить заказ. Попробуйте ещё раз или позвоните нам: ${SITE.phone}`
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <div className="space-y-1.5">
        <Label htmlFor="order-name">Имя</Label>
        <Input
          id="order-name"
          name="name"
          autoComplete="name"
          placeholder="Как к вам обращаться"
          value={name}
          onChange={(e) => setName(e.target.value)}
          aria-invalid={Boolean(errors.name)}
        />
        {errors.name && <p className="text-xs text-destructive">{errors.name}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="order-phone">Телефон</Label>
        <Input
          id="order-phone"
          name="phone"
          type="tel"
          inputMode="tel"
          autoComplete="tel"
          placeholder="+7 (___) ___-__-__"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          aria-invalid={Boolean(errors.phone)}
        />
        {errors.phone && <p className="text-xs text-destructive">{errors.phone}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="order-address">Адрес доставки</Label>
        <Input
          id="order-address"
          name="address"
          autoComplete="street-address"
          placeholder="Улица, дом, квартира"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          aria-invalid={Boolean(errors.address)}
        />
        {errors.address && (
          <p className="text-xs text-destructive">{errors.address}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label>Оплата</Label>
        <RadioGroup
          value={payment}
          onValueChange={(value) => setPayment(value as PaymentMethod)}
          className="grid grid-cols-2 gap-2"
        >
          <Label
            htmlFor="payment-cash"
            className="flex cursor-pointer items-center gap-2 rounded-md border bg-secondary/50 px-3 py-3 has-[[data-state=checked]]:border-primary"
          >
            <RadioGroupItem value="cash" id="payment-cash" />
            Наличные
          </Label>
          <Label
            htmlFor="payment-card"
            className="flex cursor-pointer items-center gap-2 rounded-md border bg-secondary/50 px-3 py-3 has-[[data-state=checked]]:border-primary"
          >
            <RadioGroupItem value="card" id="payment-card" />
            Картой курьеру
          </Label>
        </RadioGroup>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="order-comment">
          Комментарий{" "}
          <span className="font-normal text-muted-foreground">(необязательно)</span>
        </Label>
        <Input
          id="order-comment"
          name="comment"
          placeholder="Домофон, подъезд, пожелания"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
      </div>

      {submitError && (
        <p className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          {submitError}
        </p>
      )}

      <div className="mt-2 flex flex-col gap-2">
        <Button type="submit" size="lg" disabled={submitting}>
          {submitting ? (
            <>
              <Loader2 className="animate-spin" />
              Отправляем…
            </>
          ) : (
            <>Заказать за {formatPrice(totalPrice)}</>
          )}
        </Button>
        <Button type="button" variant="ghost" onClick={onBack} disabled={submitting}>
          Назад к корзине
        </Button>
      </div>
    </form>
  );
}
