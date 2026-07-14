export interface Category {
  id: string;
  title: string;
}

export interface Product {
  id: string;
  categoryId: string;
  name: string;
  /** Состав блюда или перечень позиций сета. */
  description: string;
  /** Вес в граммах. */
  weight: number;
  /** Цена в рублях. */
  price: number;
  /** Путь к фото в /public. Если файла нет — карточка покажет фирменную заглушку. */
  image?: string;
}

export const categories: Category[] = [
  { id: "sets", title: "Сеты" },
  { id: "rolls", title: "Роллы" },
];

export const products: Product[] = [
  // ─────────────────────────── Сеты ───────────────────────────
  {
    id: "filla-set",
    categoryId: "sets",
    name: "Филла Сет",
    description:
      "Филадельфия с икрой, Филадельфия с огурцом, Филадельфия, Фила эби, Хоккайдо",
    weight: 1040,
    price: 2600,
    image: "/products/filla-set.jpg",
  },
  {
    id: "losos-set",
    categoryId: "sets",
    name: "Лосось Сет",
    description: "Филадельфия ролл, Филадельфия с огурцом, Филла эби ролл",
    weight: 635,
    price: 1850,
    image: "/products/losos-set.jpg",
  },
  {
    id: "sakura-set",
    categoryId: "sets",
    name: "Сакура Сет",
    description: "Филадельфия с огурцом, Канада, Калифорния ролл, Хосомаки ролл",
    weight: 700,
    price: 1650,
    image: "/products/sakura-set.jpg",
  },
  {
    id: "fune-set",
    categoryId: "sets",
    name: "Фуне Сет",
    description: "Филадельфия с икрой, Сяке татаки, Канада",
    weight: 635,
    price: 1600,
    image: "/products/fune-set.jpg",
  },
  {
    id: "katana-set",
    categoryId: "sets",
    name: "Катана Сет",
    description:
      "Филадельфия, Унаги ролл, Хосомаки ролл, Ролл с креветкой, Каппа маки, Токио, Сяке бонито, Калифорния, Сливочный угорь",
    weight: 1500,
    price: 3400,
    image: "/products/katana-set.jpg",
  },
  {
    id: "razminka-set",
    categoryId: "sets",
    name: "Разминка Сет",
    description:
      "Канада ролл, Калифорния с креветкой, Калифорния с лососем, Хоккайдо",
    weight: 370,
    price: 900,
    image: "/products/razminka-set.jpg",
  },
  {
    id: "tempura-set",
    categoryId: "sets",
    name: "Темпура Сет",
    description: "Унаги темпура, Ниватори темпура, Цезарь темпура",
    weight: 640,
    price: 1200,
    image: "/products/tempura-set.jpg",
  },
  {
    id: "ebi-set",
    categoryId: "sets",
    name: "Эби Сет",
    description:
      "Роллы: Эби темпура, Эби тортилья, Калифорния эби, Эби роял",
    weight: 810,
    price: 1690,
    image: "/products/ebi-set.jpg",
  },
  {
    id: "vse-vklyucheno-set",
    categoryId: "sets",
    name: "Все включено Сет",
    description:
      "Филадельфия, Филадельфия с огурцом, Филадельфия роял, Филадельфия с икрой, Сегун, Уна, Дракон, Лава, Калифорния эби, Калифорния с лососем, Калифорния краб, Токио, Тануки, Харуки, Хоккайдо, Гейша, Самурай, Осако, Хияши, Ролл с лососем, Ролл с креветкой, Хосомаки, Унаги",
    weight: 3900,
    price: 8290,
    image: "/products/vse-vklyucheno-set.jpg",
  },
  {
    id: "duet-set",
    categoryId: "sets",
    name: "Дуэт Сет",
    description:
      "Хоккайдо, Калифорния с лососем, Хосомаки ролл, Сяке суши, Унаги суши, Сяке спайси, Унаги спайси",
    weight: 600,
    price: 1450,
    image: "/products/duet-set.jpg",
  },
  {
    id: "dinamit-set",
    categoryId: "sets",
    name: "Динамит Сет",
    description: "Уда ролл, Хосомаки ролл, Гейша маки, Каппа маки",
    weight: 585,
    price: 1200,
    image: "/products/dinamit-set.jpg",
  },
  {
    id: "miguri-set",
    categoryId: "sets",
    name: "Мигури Сет",
    description:
      "Филадельфия, Калифорния, Хосомаки, Унаги, Мидзу эби, Токио",
    weight: 920,
    price: 2190,
    image: "/products/miguri-set.jpg",
  },
  {
    id: "fudzi-set",
    categoryId: "sets",
    name: "Фудзи Сет",
    description:
      "Унаги ролл, Калифорния с крабом, Хоккайдо, Калифорния темпура",
    weight: 700,
    price: 1450,
    image: "/products/fudzi-set.jpg",
  },
  {
    id: "mini-set",
    categoryId: "sets",
    name: "Мини Сет",
    description: "Каппа маки, Унаги ролл, Ролл с лососем",
    weight: 340,
    price: 550,
    image: "/products/mini-set.jpg",
  },
  {
    id: "tokio-set",
    categoryId: "sets",
    name: "Токио Сет",
    description: "Сегун, Токио, Калифорния эби, Филадельфия роял",
    weight: 750,
    price: 1650,
    image: "/products/tokio-set.jpg",
  },
  {
    id: "ust-kut-set",
    categoryId: "sets",
    name: "Усть-Кут Сет",
    description: "Фила ролл, Канада, Ниватори темпура, Цунами темпура",
    weight: 900,
    price: 1800,
    image: "/products/ust-kut-set.jpg",
  },
  {
    id: "big-kush-set",
    categoryId: "sets",
    name: "Биг куш Сет",
    description:
      "Канада ролл, Калифорния, Филадельфия с огурцом, Ниватори темпура, Унаги темпура, Цунами темпура",
    weight: 1320,
    price: 2650,
    image: "/products/big-kush-set.jpg",
  },

  // ─────────────────────────── Роллы ───────────────────────────
  {
    id: "filadelfiya",
    categoryId: "rolls",
    name: "Филадельфия",
    description: "Суши рис, Сливочный сыр, Лосось",
    weight: 200,
    price: 550,
    image: "/products/filadelfiya.jpg",
  },
  {
    id: "fila-ebi",
    categoryId: "rolls",
    name: "Фила эби",
    description: "Суши рис, Лосось, Сливочный сыр, Креветка, Нори",
    weight: 215,
    price: 560,
    image: "/products/fila-ebi.jpg",
  },
  {
    id: "filadelfiya-s-ikroy",
    categoryId: "rolls",
    name: "Филадельфия с икрой",
    description: "Суши рис, Филе лосося, Икра, Сливочный сыр, Нори",
    weight: 225,
    price: 600,
    image: "/products/filadelfiya-s-ikroy.jpg",
  },
  {
    id: "filadelfiya-s-ogurcom",
    categoryId: "rolls",
    name: "Филадельфия с огурцом",
    description: "Суши рис, Сливочный сыр, Лосось, Огурец, Нори",
    weight: 220,
    price: 560,
    image: "/products/filadelfiya-s-ogurcom.jpg",
  },
  {
    id: "hokkaido",
    categoryId: "rolls",
    name: "Хоккайдо",
    description: "Суши рис, Сливочный сыр, Огурец, Лосось, Нори",
    weight: 180,
    price: 480,
    image: "/products/hokkaido.jpg",
  },
  {
    id: "filadelfiya-tataki",
    categoryId: "rolls",
    name: "Филадельфия татаки",
    description:
      "Суши рис, Сыр, Лосось опаленный открытым огнем, Нори, Огурцы, Спайси соус, Унаги соус",
    weight: 190,
    price: 495,
    image: "/products/filadelfiya-tataki.jpg",
  },
  {
    id: "filadelfiya-royal",
    categoryId: "rolls",
    name: "Филадельфия роял",
    description: "Суши рис, Сыр, Огурец, Майонез, Крабовые палочки, Нори",
    weight: 205,
    price: 530,
    image: "/products/filadelfiya-royal.jpg",
  },
  {
    id: "filadelfiya-de-lyuks",
    categoryId: "rolls",
    name: "Филадельфия де люкс",
    description: "Суши рис, Сыр, Лосось, Тобико, Нори",
    weight: 200,
    price: 560,
    image: "/products/filadelfiya-de-lyuks.jpg",
  },
  {
    id: "kaliforniya-ebi",
    categoryId: "rolls",
    name: "Калифорния эби",
    description: "Суши рис, Креветка, Майонез, Огурец, Тобико, Нори",
    weight: 185,
    price: 420,
    image: "/products/kaliforniya-ebi.jpg",
  },
  {
    id: "kaliforniya-krab",
    categoryId: "rolls",
    name: "Калифорния краб",
    description: "Суши рис, Снежный краб, Майонез, Огурец, Тобико, Нори",
    weight: 180,
    price: 390,
    image: "/products/kaliforniya-krab.jpg",
  },
  {
    id: "piramida",
    categoryId: "rolls",
    name: "Пирамида",
    description: "Суши рис, Лосось, Огурец, Сливочный сыр, Тобико, Нори",
    weight: 190,
    price: 420,
    image: "/products/piramida.jpg",
  },
  {
    id: "kaliforniya-s-lososem",
    categoryId: "rolls",
    name: "Калифорния с лососем",
    description: "Суши рис, Лосось, Огурец, Тобико, Майонез, Нори",
    weight: 180,
    price: 430,
    image: "/products/kaliforniya-s-lososem.jpg",
  },
  {
    id: "samuray",
    categoryId: "rolls",
    name: "Самурай",
    description:
      "Суши рис, Креветка тигровая, Сливочный сыр, Огурец, Тобико черный, Лосось",
    weight: 190,
    price: 450,
    image: "/products/samuray.jpg",
  },
  {
    id: "geysha-maki",
    categoryId: "rolls",
    name: "Гейша маки",
    description: "Суши рис, Тобико, Огурец, Лосось, Сыр, Нори",
    weight: 200,
    price: 510,
    image: "/products/geysha-maki.jpg",
  },
  {
    id: "syake-tataki",
    categoryId: "rolls",
    name: "Сяке татаки",
    description:
      "Суши рис, Лосось опаленный открытым огнем, Крабовые палочки, Огурец, Тобико, Нори",
    weight: 215,
    price: 530,
    image: "/products/syake-tataki.jpg",
  },
  {
    id: "ebi-royal",
    categoryId: "rolls",
    name: "Эби роял",
    description:
      "Суши рис, Лосось, Огурец, Сливочный сыр, Креветка тигровая",
    weight: 175,
    price: 440,
    image: "/products/ebi-royal.jpg",
  },
];

export function getProductsByCategory(categoryId: string): Product[] {
  return products.filter((p) => p.categoryId === categoryId);
}
