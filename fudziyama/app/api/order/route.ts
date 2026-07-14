import { NextResponse } from "next/server";

import { products } from "@/lib/products";

interface OrderItemPayload {
  id: string;
  quantity: number;
}

interface OrderPayload {
  customer: {
    name: string;
    phone: string;
    address: string;
    payment: "cash" | "card";
    comment?: string;
  };
  items: OrderItemPayload[];
}

function generateOrderId(): string {
  return `FJ-${Date.now().toString(36).toUpperCase()}`;
}

function badRequest(error: string) {
  return NextResponse.json({ ok: false, error }, { status: 400 });
}

export async function POST(request: Request) {
  let payload: OrderPayload;
  try {
    payload = await request.json();
  } catch {
    return badRequest("Некорректный формат запроса");
  }

  const { customer, items } = payload ?? {};
  if (!customer?.name?.trim()) return badRequest("Не указано имя");
  if (!customer?.phone?.replace(/\D/g, "")) return badRequest("Не указан телефон");
  if (!customer?.address?.trim()) return badRequest("Не указан адрес доставки");
  if (customer.payment !== "cash" && customer.payment !== "card") {
    return badRequest("Не выбран способ оплаты");
  }
  if (!Array.isArray(items) || items.length === 0) {
    return badRequest("Корзина пуста");
  }

  // Цены и названия берём из каталога на сервере — данным клиента не доверяем.
  const orderLines: { name: string; quantity: number; sum: number }[] = [];
  for (const item of items) {
    const product = products.find((p) => p.id === item.id);
    const quantity = Math.floor(Number(item.quantity));
    if (!product || !Number.isFinite(quantity) || quantity < 1 || quantity > 99) {
      return badRequest("В корзине есть недоступная позиция");
    }
    orderLines.push({
      name: product.name,
      quantity,
      sum: product.price * quantity,
    });
  }
  const total = orderLines.reduce((sum, line) => sum + line.sum, 0);

  const orderId = generateOrderId();
  const paymentLabel =
    customer.payment === "cash" ? "Наличные" : "Картой курьеру";

  const message = [
    `🍣 Новый заказ ${orderId}`,
    ``,
    ...orderLines.map(
      (line) => `• ${line.name} × ${line.quantity} — ${line.sum} ₽`
    ),
    ``,
    `Итого: ${total} ₽`,
    `Оплата: ${paymentLabel}`,
    ``,
    `Имя: ${customer.name.trim()}`,
    `Телефон: ${customer.phone.trim()}`,
    `Адрес: ${customer.address.trim()}`,
    customer.comment?.trim() ? `Комментарий: ${customer.comment.trim()}` : null,
  ]
    .filter((line): line is string => line !== null)
    .join("\n");

  // Уведомление о заказе в Telegram: задайте TELEGRAM_BOT_TOKEN и
  // TELEGRAM_CHAT_ID в .env.local, и каждый заказ будет приходить в чат.
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (botToken && chatId) {
    const response = await fetch(
      `https://api.telegram.org/bot${botToken}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, text: message }),
      }
    );
    if (!response.ok) {
      console.error(`[order] Telegram error for ${orderId}:`, await response.text());
      return NextResponse.json(
        { ok: false, error: "Не удалось передать заказ, позвоните нам" },
        { status: 502 }
      );
    }
  } else {
    // Без настроенного Telegram заказ фиксируется в логах сервера.
    console.log(`[order] ${orderId}\n${message}`);
  }

  return NextResponse.json({ ok: true, orderId, total });
}
