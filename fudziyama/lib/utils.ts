import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(price: number): string {
  return `${price.toLocaleString("ru-RU")} ₽`;
}

export function formatWeight(grams: number): string {
  return `${grams.toLocaleString("ru-RU")} г`;
}

/** Оставляет только цифры и проверяет российский номер телефона. */
export function isValidRussianPhone(raw: string): boolean {
  const digits = raw.replace(/\D/g, "");
  if (digits.length === 11 && (digits.startsWith("7") || digits.startsWith("8"))) return true;
  if (digits.length === 10 && digits.startsWith("9")) return true;
  return false;
}
