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
  /** Вес в граммах (если позиция измеряется весом). */
  weight?: number;
  /** Порция для штучных позиций, например «7 шт.». */
  portion?: string;
  /** Цена в рублях. */
  price: number;
}

export const categories: Category[] = [
  { id: "sets", title: "Сеты" },
  { id: "rolls", title: "Роллы" },
  { id: "tempura", title: "Темпура роллы" },
  { id: "sushi", title: "Суши и гунканы" },
  { id: "burgers", title: "Бургеры и шаурма" },
  { id: "snacks", title: "Закуски" },
  { id: "extras", title: "Соусы и добавки" },
];

/** Путь к картинке товара в /public. Замените файл на настоящее фото блюда с тем же именем. */
export function productImage(product: Product): string {
  return `/products/${product.id}.svg`;
}

export const products: Product[] = [
  // ─────────────────────────── Сеты ───────────────────────────
  { id: "filla-set", categoryId: "sets", name: "Филла Сет", description: "Филадельфия с икрой, Филадельфия с огурцом, Филадельфия, Фила эби, Хоккайдо", weight: 1040, price: 2600 },
  { id: "losos-set", categoryId: "sets", name: "Лосось Сет", description: "Филадельфия ролл, Филадельфия с огурцом, Филла эби ролл", weight: 635, price: 1850 },
  { id: "sakura-set", categoryId: "sets", name: "Сакура Сет", description: "Филадельфия с огурцом, Канада, Калифорния ролл, Хосомаки ролл", weight: 700, price: 1650 },
  { id: "fune-set", categoryId: "sets", name: "Фуне Сет", description: "Филадельфия с икрой, Сяке татаки, Канада", weight: 635, price: 1600 },
  { id: "katana-set", categoryId: "sets", name: "Катана Сет", description: "Филадельфия, Унаги ролл, Хосомаки ролл, Ролл с креветкой, Каппа маки, Токио, Сяке бонито, Калифорния, Сливочный угорь", weight: 1500, price: 3400 },
  { id: "razminka-set", categoryId: "sets", name: "Разминка Сет", description: "Канада ролл, Калифорния с креветкой, Калифорния с лососем, Хоккайдо", weight: 370, price: 900 },
  { id: "tempura-set", categoryId: "sets", name: "Темпура Сет", description: "Унаги темпура, Ниватори темпура, Цезарь темпура", weight: 640, price: 1200 },
  { id: "ebi-set", categoryId: "sets", name: "Эби Сет", description: "Роллы: Эби темпура, Эби тортилья, Калифорния эби, Эби роял", weight: 810, price: 1690 },
  { id: "vse-vklyucheno-set", categoryId: "sets", name: "Все включено Сет", description: "Филадельфия, Филадельфия с огурцом, Филадельфия роял, Филадельфия с икрой, Сегун, Уна, Дракон, Лава, Калифорния эби, Калифорния с лососем, Калифорния краб, Токио, Тануки, Харуки, Хоккайдо, Гейша, Самурай, Осако, Хияши, Ролл с лососем, Ролл с креветкой, Хосомаки, Унаги", weight: 3900, price: 8290 },
  { id: "duet-set", categoryId: "sets", name: "Дуэт Сет", description: "Хоккайдо, Калифорния с лососем, Хосомаки ролл, Сяке суши, Унаги суши, Сяке спайси, Унаги спайси", weight: 600, price: 1450 },
  { id: "dinamit-set", categoryId: "sets", name: "Динамит Сет", description: "Уда ролл, Хосомаки ролл, Гейша маки, Каппа маки", weight: 585, price: 1200 },
  { id: "miguri-set", categoryId: "sets", name: "Мигури Сет", description: "Филадельфия, Калифорния, Хосомаки, Унаги, Мидзу эби, Токио", weight: 920, price: 2190 },
  { id: "fudzi-set", categoryId: "sets", name: "Фудзи Сет", description: "Унаги ролл, Калифорния с крабом, Хоккайдо, Калифорния темпура", weight: 700, price: 1450 },
  { id: "mini-set", categoryId: "sets", name: "Мини Сет", description: "Каппа маки, Унаги ролл, Ролл с лососем", weight: 340, price: 550 },
  { id: "tokio-set", categoryId: "sets", name: "Токио Сет", description: "Сегун, Токио, Калифорния эби, Филадельфия роял", weight: 750, price: 1650 },
  { id: "ust-kut-set", categoryId: "sets", name: "Усть-Кут Сет", description: "Фила ролл, Канада, Ниватори темпура, Цунами темпура", weight: 900, price: 1800 },
  { id: "big-kush-set", categoryId: "sets", name: "Биг куш Сет", description: "Канада ролл, Калифорния, Филадельфия с огурцом, Ниватори темпура, Унаги темпура, Цунами темпура", weight: 1320, price: 2650 },

  // ─────────────────────────── Роллы ───────────────────────────
  { id: "filadelfiya", categoryId: "rolls", name: "Филадельфия", description: "Суши рис, Сливочный сыр, Лосось", weight: 200, price: 550 },
  { id: "fila-ebi", categoryId: "rolls", name: "Фила эби", description: "Суши рис, Лосось, Сливочный сыр, Креветка, Нори", weight: 215, price: 560 },
  { id: "filadelfiya-s-ikroy", categoryId: "rolls", name: "Филадельфия с икрой", description: "Суши рис, Филе лосося, Икра, Сливочный сыр, Нори", weight: 225, price: 600 },
  { id: "filadelfiya-s-ogurcom", categoryId: "rolls", name: "Филадельфия с огурцом", description: "Суши рис, Сливочный сыр, Лосось, Огурец, Нори", weight: 220, price: 560 },
  { id: "hokkaido", categoryId: "rolls", name: "Хоккайдо", description: "Суши рис, Сливочный сыр, Огурец, Лосось, Нори", weight: 180, price: 480 },
  { id: "filadelfiya-tataki", categoryId: "rolls", name: "Филадельфия татаки", description: "Суши рис, Сыр, Лосось опаленный открытым огнем, Нори, Огурцы, Спайси соус, Унаги соус", weight: 190, price: 495 },
  { id: "filadelfiya-royal", categoryId: "rolls", name: "Филадельфия роял", description: "Суши рис, Сыр, Огурец, Майонез, Крабовые палочки, Нори", weight: 205, price: 530 },
  { id: "filadelfiya-de-lyuks", categoryId: "rolls", name: "Филадельфия де люкс", description: "Суши рис, Сыр, Лосось, Тобико, Нори", weight: 200, price: 560 },
  { id: "kaliforniya-ebi", categoryId: "rolls", name: "Калифорния эби", description: "Суши рис, Креветка, Майонез, Огурец, Тобико, Нори", weight: 185, price: 420 },
  { id: "kaliforniya-krab", categoryId: "rolls", name: "Калифорния краб", description: "Суши рис, Снежный краб, Майонез, Огурец, Тобико, Нори", weight: 180, price: 390 },
  { id: "piramida", categoryId: "rolls", name: "Пирамида", description: "Суши рис, Лосось, Огурец, Сливочный сыр, Тобико, Нори", weight: 190, price: 420 },
  { id: "kaliforniya-s-lososem", categoryId: "rolls", name: "Калифорния с лососем", description: "Суши рис, Лосось, Огурец, Тобико, Майонез, Нори", weight: 180, price: 430 },
  { id: "samuray", categoryId: "rolls", name: "Самурай", description: "Суши рис, Креветка тигровая, Сливочный сыр, Огурец, Тобико черный, Лосось", weight: 190, price: 450 },
  { id: "geysha-maki", categoryId: "rolls", name: "Гейша маки", description: "Суши рис, Тобико, Огурец, Лосось, Сыр, Нори", weight: 200, price: 510 },
  { id: "syake-tataki", categoryId: "rolls", name: "Сяке татаки", description: "Суши рис, Лосось опаленный открытым огнем, Крабовые палочки, Огурец, Тобико, Нори", weight: 215, price: 530 },
  { id: "ebi-royal", categoryId: "rolls", name: "Эби роял", description: "Суши рис, Лосось, Огурец, Сливочный сыр, Креветка тигровая", weight: 175, price: 440 },
  { id: "bonita", categoryId: "rolls", name: "Бонита", description: "Суши рис, Огурец, Майонез, Тобико, Угорь, Стружка тунца", weight: 170, price: 430 },
  { id: "syake-bonita", categoryId: "rolls", name: "Сяке бонита", description: "Суши рис, Сыр, Огурец, Лосось, Нори", weight: 180, price: 460 },
  { id: "drakon", categoryId: "rolls", name: "Дракон", description: "Суши рис, Нори, Спайси соус, Огурец, Лист салата, Курица, Угорь, Унаги соус, Кунжут, Опаленный огнем", weight: 250, price: 480 },
  { id: "slivochnyy-ugor", categoryId: "rolls", name: "Сливочный угорь", description: "Суши рис, Сыр, Угорь, Тобико, Унаги соус, Кунжут, Огурец, Нори", weight: 200, price: 450 },
  { id: "geysha", categoryId: "rolls", name: "Гейша", description: "Суши рис, Сыр, Огурец, Тобико красный, Лосось, Нори", weight: 170, price: 450 },
  { id: "ikura-unagi", categoryId: "rolls", name: "Икура унаги", description: "Суши рис, Сыр, Огурец, Краб, Угорь, Икра, Нори", weight: 210, price: 530 },
  { id: "segun", categoryId: "rolls", name: "Сегун", description: "Суши рис, Сыр, Угорь, Огурец, Унаги соус, Кунжут, Нори", weight: 190, price: 430 },
  { id: "una", categoryId: "rolls", name: "Уна", description: "Суши рис, Сыр, Лосось, Огурец, Унаги соус, Кунжут", weight: 195, price: 460 },
  { id: "banzay", categoryId: "rolls", name: "Банзай", description: "Суши рис, Сливочный сыр, Огурец, Лосось, Спайси соус", weight: 195, price: 450 },
  { id: "minamit-maki", categoryId: "rolls", name: "Минамит маки", description: "Суши рис, Угорь, Огурец, Лосось, Сливочный сыр, Нори", weight: 170, price: 400 },
  { id: "toyama", categoryId: "rolls", name: "Тояма", description: "Суши рис, Сливочный сыр, Тобико, Огурец, Креветка тигровая, Кунжут", weight: 185, price: 450 },
  { id: "tokio", categoryId: "rolls", name: "Токио", description: "Суши рис, Лосось, Спайс соус, Огурец, Краб, Тобико черный, Нори", weight: 170, price: 430 },
  { id: "tortilya", categoryId: "rolls", name: "Тортилья", description: "Суши рис, Огурец, Помидор, Куриное филе, Сыр, Тортилья, Нори", weight: 190, price: 390 },
  { id: "syake-tortilya", categoryId: "rolls", name: "Сяке тортилья", description: "Суши рис, Сливочный сыр, Огурец, Тортилья, Лосось, Лист салата, Нори", weight: 190, price: 400 },
  { id: "hiyashchi", categoryId: "rolls", name: "Хиящи", description: "Суши рис, Лосось, Огурец, Нори, Спайси соус, Кунжут", weight: 170, price: 390 },
  { id: "ikura", categoryId: "rolls", name: "Икура", description: "Суши рис, Лосось, Огурец, Сыр, Икра лосося, Нори", weight: 170, price: 400 },
  { id: "osako", categoryId: "rolls", name: "Осако", description: "Суши рис, Огурец, Лосось, Майонез, Кунжут, Нори", weight: 170, price: 370 },
  { id: "amori", categoryId: "rolls", name: "Амори", description: "Суши рис, Нори, Сыр, Огурец, Тобико красный, Лосось опаленный открытым огнем", weight: 190, price: 480 },
  { id: "agacu", categoryId: "rolls", name: "Агацу", description: "Суши рис, Угорь, Огурец, Лосось, Спайси соус, Нори", weight: 185, price: 420 },
  { id: "niku-maki", categoryId: "rolls", name: "Нику маки", description: "Суши рис, Сыр, Огурец, Лосось, Гребешок, Нори, Спайси соус, Кунжут", weight: 220, price: 480 },
  { id: "lava", categoryId: "rolls", name: "Лава", description: "Суши рис, Лосось гриль, Огурец, Майонез, Гребешок, Тобико, Нори", weight: 190, price: 460 },
  { id: "magura", categoryId: "rolls", name: "Магура", description: "Суши рис, Сыр, Огурец, Угорь, Курица, Майонез, Тобико, Кунжут, Унаги соус", weight: 195, price: 400 },
  { id: "vulkan", categoryId: "rolls", name: "Вулкан", description: "Суши рис, Гребешок, Лосось, Майонез, Сливочный сыр, Тобико, Унаги соус, Огурец, Нори", weight: 185, price: 460 },
  { id: "sensey", categoryId: "rolls", name: "Сенсей", description: "Суши рис, Креветки, Спайси соус, Лист салата, Огурец, Нори", weight: 210, price: 450 },
  { id: "roll-s-lososem", categoryId: "rolls", name: "Ролл с лососем", description: "Суши рис, Огурец, Лосось, Сливочный сыр, Нори", weight: 130, price: 270 },
  { id: "ostryy-losos", categoryId: "rolls", name: "Острый лосось", description: "Суши рис, Огурец, Лосось, Спайси соус, Нори", weight: 130, price: 270 },
  { id: "roll-s-krabom", categoryId: "rolls", name: "Ролл с крабом", description: "Суши рис, Сливочный сыр, Огурец, Снежный краб, Нори", weight: 130, price: 260 },
  { id: "roll-s-krevetkoy", categoryId: "rolls", name: "Ролл с креветкой", description: "Суши рис, Сливочный сыр, Огурец, Креветка, Нори", weight: 130, price: 270 },
  { id: "unagi", categoryId: "rolls", name: "Унаги", description: "Суши рис, Огурец, Угорь, Унаги соус, Кунжут, Нори", weight: 130, price: 270 },
  { id: "kappa-maki", categoryId: "rolls", name: "Каппа маки", description: "Суши рис, Огурец, Кунжут, Нори", weight: 100, price: 150 },

  // ─────────────────────────── Темпура роллы ───────────────────────────
  { id: "ebi-tortilya", categoryId: "tempura", name: "Эби тортилья", description: "Суши рис, Нори, Сыр, Огурец, Креветка, Тортилья, Кляр, Сухари", weight: 240, price: 460 },
  { id: "kaliforniya-tempura", categoryId: "tempura", name: "Калифорния темпура", description: "Суши рис, Лосось, Сливочный сыр, Огурец, Крабовые палочки, Кляр, Сухари, Нори", weight: 210, price: 420 },
  { id: "cunami-tempura", categoryId: "tempura", name: "Цунами темпура", description: "Суши рис, Сливочный сыр, Лосось, Огурец, Кляр, Сухари, Тортилья, Нори", weight: 240, price: 430 },
  { id: "filadelfiya-tempura", categoryId: "tempura", name: "Филадельфия темпура", description: "Суши рис, Лосось, Сливочный сыр, Кляр, Сухари, Нори", weight: 240, price: 560 },
  { id: "minamit-tempura", categoryId: "tempura", name: "Минамит темпура", description: "Суши рис, Угорь, Лосось, Кляр, Сыр, Сухари, Нори", weight: 200, price: 450 },
  { id: "cezar-tempura", categoryId: "tempura", name: "Цезарь темпура", description: "Суши рис, Куриное филе, Сыр, Тобико, Кляр, Огурец, Сухари, Лист салата, Нори", weight: 220, price: 420 },
  { id: "nivatori-tempura", categoryId: "tempura", name: "Ниватори темпура", description: "Суши рис, Лосось, Огурец, Тобико, Сливочный сыр, Кляр, Сухари, Нори", weight: 210, price: 440 },
  { id: "unagi-tempura", categoryId: "tempura", name: "Унаги темпура", description: "Суши рис, Сливочный сыр, Угорь, Огурец, Тобико, Кляр, Сухари, Нори", weight: 210, price: 450 },
  { id: "ebi-tempura", categoryId: "tempura", name: "Эби темпура", description: "Суши рис, Сливочный сыр, Креветка, Огурец, Кляр, Сухари, Нори", weight: 210, price: 450 },
  { id: "salamonskiy-tempura", categoryId: "tempura", name: "Саламонский темпура", description: "Суши рис, Сыр, Огурец, Тобико, Снежный краб, Кляр, Сухари", weight: 210, price: 410 },

  // ─────────────────────────── Суши и гунканы ───────────────────────────
  { id: "syake-spays", categoryId: "sushi", name: "Сяке спайс", description: "Суши рис, Нори, Лосось, Спайси соус", weight: 30, price: 130 },
  { id: "ebi-spays", categoryId: "sushi", name: "Эби спайс", description: "Суши рис, Нори, Креветка, Спайси соус", weight: 30, price: 130 },
  { id: "unagi-spaysi", categoryId: "sushi", name: "Унаги спайси", description: "Суши рис, Нори, Угорь, Спайси соус", weight: 30, price: 130 },
  { id: "kani-spaysi", categoryId: "sushi", name: "Кани спайси", description: "Суши рис, Нори, Снежный краб, Спайси соус", weight: 30, price: 120 },
  { id: "ebi-maki-gunkan", categoryId: "sushi", name: "Эби маки", description: "Суши рис, Нори, Огурец, Тобико, Майонез", weight: 35, price: 130 },
  { id: "syake-maki-gunkan", categoryId: "sushi", name: "Сяке маки", description: "Суши рис, Нори, Лосось, Майонез", weight: 30, price: 130 },
  { id: "ikura-gunkan", categoryId: "sushi", name: "Икура гункан", description: "Суши рис, Нори, Икра лосося", weight: 50, price: 190 },
  { id: "hatate-spaysi", categoryId: "sushi", name: "Хатате спайси", description: "Суши рис, Нори, Гребешок, Спайси соус", weight: 30, price: 120 },
  { id: "unagi-sushi", categoryId: "sushi", name: "Унаги суши", description: "Суши рис, Нори, Угорь, Унаги соус, Кунжут", weight: 30, price: 130 },
  { id: "syake-sushi", categoryId: "sushi", name: "Сяке суши", description: "Суши рис, Лосось", weight: 28, price: 130 },
  { id: "ebi-sushi", categoryId: "sushi", name: "Эби суши", description: "Суши рис, Креветка", weight: 27, price: 130 },

  // ─────────────────────────── Бургеры и шаурма ───────────────────────────
  { id: "dvoynoy-chizburger", categoryId: "burgers", name: "Двойной чизбургер", description: "Две говяжьи котлеты, Булочка, Лист салата, Помидоры, Корнишон, Сыр, Соус сырный, Соус барбекю", weight: 300, price: 480 },
  { id: "chiken-burger", categoryId: "burgers", name: "Чикен бургер", description: "Котлета куриная, Лист салата, Булочка, Огурцы, Помидоры, Соус барбекю, Соус сырный", weight: 270, price: 330 },
  { id: "chizburger", categoryId: "burgers", name: "Чизбургер", description: "Котлета говяжья, Булочка, Лист салата, Корнишон, Помидоры, Сырный соус, Соус барбекю", weight: 270, price: 360 },
  { id: "burger-s-krevetkoy", categoryId: "burgers", name: "Бургер с креветкой", description: "Креветки, Булочка, Лист салата, Помидор, Огурцы, Соус сырный, Соус барбекю", weight: 270, price: 400 },
  { id: "shaurma-s-kuricey", categoryId: "burgers", name: "Шаурма с курицей", description: "Помидоры, Огурцы, Капуста, Курица, Чесночный соус, Томатный соус, Лаваш", weight: 360, price: 350 },
  { id: "shaurma-s-krevetkoy", categoryId: "burgers", name: "Шаурма с креветкой", description: "Помидоры, Огурцы, Капуста, Креветка в панировке, Лаваш, Чесночный соус, Томатный соус", weight: 380, price: 380 },

  // ─────────────────────────── Закуски ───────────────────────────
  { id: "stripsy", categoryId: "snacks", name: "Стрипсы", description: "Куриные стрипсы в хрустящей панировке", portion: "7 шт.", price: 350 },
  { id: "kartofel-po-derevenski", categoryId: "snacks", name: "Картофель по-деревенски", description: "Румяные дольки картофеля со специями", weight: 180, price: 330 },
  { id: "krylyshki", categoryId: "snacks", name: "Крылышки", description: "Куриные крылышки в хрустящей панировке", portion: "12 шт.", price: 1190 },
  { id: "basket-miks", categoryId: "snacks", name: "Баскет Микс", description: "Крылышки 9 шт., Стрипсы 9 шт.", portion: "18 шт.", price: 1390 },
  { id: "kartofel-fri", categoryId: "snacks", name: "Картофель фри", description: "Классический картофель фри", weight: 200, price: 300 },
  { id: "naggetsy", categoryId: "snacks", name: "Наггетсы", description: "Куриные наггетсы в панировке", portion: "9 шт.", price: 310 },
  { id: "krevetki-v-klyare", categoryId: "snacks", name: "Креветки в кляре", description: "Креветки в хрустящем кляре", portion: "7 шт.", price: 350 },
  { id: "syrnye-shariki", categoryId: "snacks", name: "Сырные шарики", description: "Шарики из сыра в панировке", portion: "9 шт.", price: 330 },
  { id: "syrnye-palochki", categoryId: "snacks", name: "Сырные палочки", description: "Сырные палочки в хрустящей панировке", portion: "7 шт.", price: 275 },

  // ─────────────────────────── Соусы и добавки ───────────────────────────
  { id: "sous-barbekyu", categoryId: "extras", name: "Барбекю соус", description: "Соус к закускам и бургерам", price: 50 },
  { id: "sous-syrnyy", categoryId: "extras", name: "Сырный соус", description: "Соус к закускам и бургерам", price: 50 },
  { id: "sous-chesnochnyy", categoryId: "extras", name: "Чесночный соус", description: "Соус к закускам и бургерам", price: 50 },
  { id: "sous-tomatnyy", categoryId: "extras", name: "Томатный соус", description: "Соус к закускам и бургерам", price: 35 },
  { id: "soevyy-sous", categoryId: "extras", name: "Соевый соус", description: "Классический соевый соус к суши и роллам", price: 30 },
  { id: "imbir", categoryId: "extras", name: "Имбирь", description: "Маринованный имбирь", price: 20 },
  { id: "vasabi", categoryId: "extras", name: "Васаби", description: "Острая японская приправа", price: 20 },
  { id: "syr-chedder", categoryId: "extras", name: "Сыр чеддер", description: "Добавка к шаурме", weight: 25, price: 40 },
  { id: "perec-halapeno", categoryId: "extras", name: "Перец халапеньо", description: "Добавка к шаурме", weight: 15, price: 20 },
  { id: "kurinoe-myaso", categoryId: "extras", name: "Куриное мясо", description: "Добавка к шаурме", weight: 30, price: 50 },
];

export function getProductsByCategory(categoryId: string): Product[] {
  return products.filter((p) => p.categoryId === categoryId);
}
