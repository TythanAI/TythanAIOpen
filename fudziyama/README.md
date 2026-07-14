# Фудзияма — сайт доставки еды (г. Усть-Кут)

Современный минималистичный сайт доставки: Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn/ui, Zustand.

## Запуск

```bash
npm install
npm run dev      # разработка — http://localhost:3000
npm run build    # продакшен-сборка
npm start        # запуск продакшен-сервера
```

## Приём заказов в Telegram

Форма заказа отправляет данные в `POST /api/order`. Чтобы заказы приходили вам в Telegram:

1. Создайте бота через [@BotFather](https://t.me/BotFather), скопируйте токен.
2. Узнайте `chat_id` чата или группы (например, через @userinfobot).
3. Скопируйте `.env.example` в `.env.local` и заполните `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`.

Без настройки Telegram заказы просто пишутся в лог сервера (сайт при этом полностью работает).

## Картинки блюд

Для каждой позиции в `public/products/<id>.svg` лежит сгенерированная векторная иллюстрация (`node scripts/generate-images.mjs` пересоздаёт их все). Чтобы поставить настоящее фото блюда, положите файл на место соответствующего SVG (или поменяйте расширение в `productImage()` в `lib/products.ts`). Картинки загружаются через skeleton-блок с плавным появлением.

## Структура

- `lib/products.ts` — каталог: категории, цены, граммовки, составы (единственное место, где меняется меню)
- `lib/site.ts` — телефон, адрес, часы работы
- `store/use-cart.ts` — корзина на Zustand (persist в localStorage)
- `components/product-card.tsx` — карточка товара с кнопкой «В корзину» → «− / +»
- `components/category-nav.tsx` — липкая панель категорий со scroll-spy
- `components/cart-sheet.tsx` — боковая панель корзины + оформление заказа
- `app/api/order/route.ts` — приём заказа (валидация и пересчёт цен на сервере)
