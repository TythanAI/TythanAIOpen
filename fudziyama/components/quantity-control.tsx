"use client";

import { Minus, Plus } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface QuantityControlProps {
  quantity: number;
  onIncrement: () => void;
  onDecrement: () => void;
  className?: string;
  size?: "sm" | "default";
}

/** Счётчик «− количество +», используется в карточке товара и в корзине. */
export function QuantityControl({
  quantity,
  onIncrement,
  onDecrement,
  className,
  size = "default",
}: QuantityControlProps) {
  const buttonSize = size === "sm" ? "h-8 w-8" : "h-10 w-10";

  return (
    <div
      className={cn(
        "flex items-center justify-between rounded-md bg-secondary",
        className
      )}
    >
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className={buttonSize}
        onClick={onDecrement}
        aria-label="Уменьшить количество"
      >
        <Minus />
      </Button>
      <span
        className="min-w-8 select-none text-center text-sm font-semibold tabular-nums"
        aria-live="polite"
      >
        {quantity}
      </span>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className={buttonSize}
        onClick={onIncrement}
        aria-label="Увеличить количество"
      >
        <Plus />
      </Button>
    </div>
  );
}
