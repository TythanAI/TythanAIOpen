// Генерирует векторные картинки блюд в public/products/<id>.svg.
// Цвета начинки берутся из состава: лосось — оранжевый, угорь — коричневый и т.д.
// Запуск: node scripts/generate-images.mjs
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(join(root, "lib/products.ts"), "utf8");
const outDir = join(root, "public/products");
mkdirSync(outDir, { recursive: true });

const items = [];
const re = /\{ id: "([^"]+)", categoryId: "([^"]+)", name: "([^"]+)", description: "([^"]*)"/g;
let m;
while ((m = re.exec(source)) !== null) {
  items.push({ id: m[1], category: m[2], name: m[3], description: m[4] });
}
if (items.length === 0) throw new Error("Не удалось прочитать каталог из lib/products.ts");

const W = 800;
const H = 600;

// Палитра начинок по ключевым словам состава.
const FILLINGS = [
  [/лосось|фила|сяке/i, "#ef8354"],
  [/угорь|унаги/i, "#8a5a3b"],
  [/креветк|эби/i, "#f2a48e"],
  [/икра|икур|тобико красный/i, "#e2503c"],
  [/краб/i, "#e87b7b"],
  [/огурец|салата|капуста/i, "#7fb069"],
  [/сыр|майонез/i, "#f2ecd8"],
  [/курица|куриное/i, "#d9a45b"],
  [/тобико черный/i, "#3d3a45"],
  [/тобико/i, "#e05d5d"],
  [/гребешок/i, "#e8d9c5"],
  [/помидор/i, "#d94f3d"],
];

function fillingsFor(description) {
  const found = [];
  for (const [pattern, color] of FILLINGS) {
    if (pattern.test(description) && !found.includes(color)) found.push(color);
  }
  return found.length > 0 ? found : ["#ef8354", "#f2ecd8"];
}

// Детерминированный псевдорандом от строки — чтобы картинки не менялись между запусками.
function rng(seed) {
  let h = 2166136261;
  for (const ch of seed) {
    h ^= ch.charCodeAt(0);
    h = Math.imul(h, 16777619);
  }
  return () => {
    h = Math.imul(h ^ (h >>> 15), 2246822519);
    h = Math.imul(h ^ (h >>> 13), 3266489917);
    return ((h ^= h >>> 16) >>> 0) / 4294967296;
  };
}

const header = (id) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">` +
  `<defs><radialGradient id="bg-${id}" cx="50%" cy="35%" r="80%">` +
  `<stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#efeff2"/>` +
  `</radialGradient></defs>` +
  `<rect width="${W}" height="${H}" fill="url(#bg-${id})"/>`;

const SHADOW = 0.1; // мягкие тени под блюдами на светлом фоне

function rollPiece(x, y, r, outer, fillings, rand, tempura) {
  const parts = [];
  parts.push(`<circle cx="${x}" cy="${y + 6}" r="${r}" fill="#000" opacity="${SHADOW}"/>`);
  const edge = tempura ? "#c08c4a" : outer === "#f5f2e8" ? "#e0d9c2" : "#1f2321";
  parts.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${outer}" stroke="${edge}" stroke-width="2"/>`);
  if (tempura) {
    // Хрустящая кромка кляра
    for (let i = 0; i < 14; i++) {
      const a = (i / 14) * Math.PI * 2 + rand();
      parts.push(
        `<circle cx="${(x + Math.cos(a) * r * 0.92).toFixed(1)}" cy="${(y + Math.sin(a) * r * 0.92).toFixed(1)}" r="${(3 + rand() * 4).toFixed(1)}" fill="#b5854e"/>`
      );
    }
    parts.push(`<circle cx="${x}" cy="${y}" r="${r * 0.72}" fill="#f5f2e8"/>`);
  } else {
    parts.push(`<circle cx="${x}" cy="${y}" r="${r * 0.86}" fill="#f5f2e8"/>`);
    // Зёрна риса
    for (let i = 0; i < 10; i++) {
      const a = rand() * Math.PI * 2;
      const d = r * (0.62 + rand() * 0.2);
      parts.push(
        `<ellipse cx="${(x + Math.cos(a) * d).toFixed(1)}" cy="${(y + Math.sin(a) * d).toFixed(1)}" rx="4" ry="2" fill="#e6e0cf" transform="rotate(${(rand() * 180).toFixed(0)} ${(x + Math.cos(a) * d).toFixed(1)} ${(y + Math.sin(a) * d).toFixed(1)})"/>`
      );
    }
  }
  // Начинка секторами
  const n = Math.min(fillings.length, 3);
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2 + rand() * 0.5;
    const d = n === 1 ? 0 : r * 0.22;
    parts.push(
      `<circle cx="${(x + Math.cos(a) * d).toFixed(1)}" cy="${(y + Math.sin(a) * d).toFixed(1)}" r="${(r * (n === 1 ? 0.4 : 0.26)).toFixed(1)}" fill="${fillings[i]}"/>`
    );
  }
  return parts.join("");
}

function rollsSvg(item, count, tempura) {
  const rand = rng(item.id);
  const fillings = fillingsFor(item.description);
  const outer = tempura
    ? "#d9a45b"
    : /нори/i.test(item.description) && rand() > 0.5
      ? "#2e3230"
      : "#f5f2e8";
  const cols = count > 6 ? 4 : 3;
  const rows = Math.ceil(count / cols);
  const r = Math.min(70, 300 / rows / 1.6);
  const parts = [header(item.id)];
  let k = 0;
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols && k < count; col++, k++) {
      const x = W / 2 + (col - (cols - 1) / 2) * (r * 2.3) + (rand() - 0.5) * 8;
      const y = H / 2 - 20 + (row - (rows - 1) / 2) * (r * 2.3) + (rand() - 0.5) * 8;
      parts.push(rollPiece(x, y, r, outer, fillings, rand, tempura));
    }
  }
  parts.push("</svg>");
  return parts.join("");
}

function gunkanSvg(item) {
  const rand = rng(item.id);
  const fillings = fillingsFor(item.description);
  const top = fillings[0];
  const cx = W / 2;
  const cy = H / 2 + 20;
  const parts = [header(item.id)];
  parts.push(`<ellipse cx="${cx}" cy="${cy + 90}" rx="150" ry="26" fill="#000" opacity="${SHADOW}"/>`);
  if (/суши рис, лосось$|суши рис, креветка$/i.test(item.description.trim())) {
    // Нигири: рис + ломтик сверху
    parts.push(`<ellipse cx="${cx}" cy="${cy + 60}" rx="140" ry="55" fill="#f5f2e8" stroke="#e0d9c2" stroke-width="2"/>`);
    parts.push(`<path d="M ${cx - 150} ${cy + 30} Q ${cx} ${cy - 60} ${cx + 150} ${cy + 30} Q ${cx} ${cy + 80} ${cx - 150} ${cy + 30} Z" fill="${top}"/>`);
    for (let i = -2; i <= 2; i++) {
      parts.push(`<path d="M ${cx + i * 40 - 20} ${cy - 20} q 20 20 40 34" stroke="#ffffff" stroke-opacity="${SHADOW}" stroke-width="5" fill="none"/>`);
    }
  } else {
    // Гункан: борт из нори + горка начинки
    parts.push(`<rect x="${cx - 120}" y="${cy - 40}" width="240" height="130" rx="40" fill="#23272a"/>`);
    for (let i = 0; i < 24; i++) {
      const a = rand() * Math.PI;
      const px = cx - 95 + rand() * 190;
      const py = cy - 40 - rand() * 28;
      parts.push(`<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${(10 + rand() * 9).toFixed(1)}" fill="${fillings[Math.floor(a) % fillings.length] ?? top}"/>`);
    }
    parts.push(`<rect x="${cx - 120}" y="${cy - 40}" width="240" height="130" rx="40" fill="none" stroke="#111" stroke-width="3"/>`);
  }
  parts.push("</svg>");
  return parts.join("");
}

function burgerSvg(item) {
  const cx = W / 2;
  const cy = H / 2 + 30;
  const shrimp = /креветк/i.test(item.description);
  const patty = shrimp ? "#e8a380" : /куриная/i.test(item.description) ? "#d9a45b" : "#6b4226";
  const parts = [header(item.id)];
  parts.push(`<ellipse cx="${cx}" cy="${cy + 110}" rx="200" ry="28" fill="#000" opacity="${SHADOW}"/>`);
  parts.push(`<path d="M ${cx - 190} ${cy - 40} Q ${cx} ${cy - 190} ${cx + 190} ${cy - 40} Z" fill="#e0913f"/>`);
  parts.push(`<circle cx="${cx - 60}" cy="${cy - 110}" r="5" fill="#f7e8c8"/><circle cx="${cx + 10}" cy="${cy - 130}" r="5" fill="#f7e8c8"/><circle cx="${cx + 70}" cy="${cy - 100}" r="5" fill="#f7e8c8"/>`);
  parts.push(`<path d="M ${cx - 190} ${cy - 40} h 380 l -22 24 -30 -16 -30 18 -30 -18 -30 18 -30 -18 -30 18 -30 -18 -30 18 -30 -16 Z" fill="#8db052"/>`);
  parts.push(`<rect x="${cx - 175}" y="${cy - 14}" width="350" height="26" rx="13" fill="#d94f3d"/>`);
  parts.push(`<rect x="${cx - 185}" y="${cy + 12}" width="370" height="20" rx="10" fill="#f2c14e"/>`);
  parts.push(`<rect x="${cx - 180}" y="${cy + 32}" width="360" height="42" rx="21" fill="${patty}"/>`);
  if (/две говяжьи/i.test(item.description)) {
    parts.push(`<rect x="${cx - 175}" y="${cy + 76}" width="350" height="16" rx="8" fill="#f2c14e"/>`);
    parts.push(`<rect x="${cx - 180}" y="${cy + 92}" width="360" height="38" rx="19" fill="${patty}"/>`);
    parts.push(`<rect x="${cx - 185}" y="${cy + 130}" width="370" height="30" rx="15" fill="#e0913f"/>`);
  } else {
    parts.push(`<rect x="${cx - 185}" y="${cy + 76}" width="370" height="34" rx="17" fill="#e0913f"/>`);
  }
  parts.push("</svg>");
  return parts.join("");
}

function shaurmaSvg(item) {
  const cx = W / 2;
  const cy = H / 2;
  const parts = [header(item.id)];
  parts.push(`<ellipse cx="${cx}" cy="${cy + 130}" rx="230" ry="30" fill="#000" opacity="${SHADOW}"/>`);
  for (const [dx, dy, rot] of [[-40, 30, -18], [50, -10, -14]]) {
    parts.push(`<g transform="rotate(${rot} ${cx + dx} ${cy + dy})">`);
    parts.push(`<rect x="${cx + dx - 190}" y="${cy + dy - 55}" width="380" height="110" rx="55" fill="#e8c07d"/>`);
    parts.push(`<rect x="${cx + dx - 190}" y="${cy + dy - 55}" width="380" height="110" rx="55" fill="none" stroke="#c99b54" stroke-width="4"/>`);
    parts.push(`<path d="M ${cx + dx - 100} ${cy + dy - 55} v 110 M ${cx + dx} ${cy + dy - 55} v 110 M ${cx + dx + 100} ${cy + dy - 55} v 110" stroke="#c99b54" stroke-width="6" opacity="0.6"/>`);
    parts.push(`<ellipse cx="${cx + dx + 190}" cy="${cy + dy}" rx="26" ry="52" fill="#b8874a"/>`);
    parts.push(`<circle cx="${cx + dx + 182}" cy="${cy + dy - 18}" r="10" fill="#7fb069"/><circle cx="${cx + dx + 194}" cy="${cy + dy + 6}" r="11" fill="#d94f3d"/><circle cx="${cx + dx + 178}" cy="${cy + dy + 24}" r="9" fill="#f2ecd8"/>`);
    parts.push("</g>");
  }
  parts.push("</svg>");
  return parts.join("");
}

const SNACK_EMOJI = {
  stripsy: "🍗",
  "kartofel-po-derevenski": "🥔",
  krylyshki: "🍗",
  "basket-miks": "🍗",
  "kartofel-fri": "🍟",
  naggetsy: "🍗",
  "krevetki-v-klyare": "🍤",
  "syrnye-shariki": "🧀",
  "syrnye-palochki": "🧀",
};

const EXTRA_COLORS = {
  "sous-barbekyu": "#6b3548",
  "sous-syrnyy": "#f2c14e",
  "sous-chesnochnyy": "#f2ecd8",
  "sous-tomatnyy": "#d94f3d",
  "soevyy-sous": "#3a2a20",
  imbir: "#f2a48e",
  vasabi: "#7fb069",
  "syr-chedder": "#f2c14e",
  "perec-halapeno": "#5a9142",
  "kurinoe-myaso": "#d9a45b",
};

function snackSvg(item) {
  const parts = [header(item.id)];
  parts.push(`<ellipse cx="${W / 2}" cy="${H / 2 + 130}" rx="170" ry="26" fill="#000" opacity="${SHADOW}"/>`);
  parts.push(`<text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle" font-size="220">${SNACK_EMOJI[item.id] ?? "🍽️"}</text>`);
  parts.push("</svg>");
  return parts.join("");
}

function extraSvg(item) {
  const color = EXTRA_COLORS[item.id] ?? "#d94f3d";
  const cx = W / 2;
  const cy = H / 2 + 10;
  const parts = [header(item.id)];
  parts.push(`<ellipse cx="${cx}" cy="${cy + 105}" rx="140" ry="24" fill="#000" opacity="${SHADOW}"/>`);
  parts.push(`<path d="M ${cx - 120} ${cy - 40} L ${cx - 100} ${cy + 95} Q ${cx} ${cy + 120} ${cx + 100} ${cy + 95} L ${cx + 120} ${cy - 40} Z" fill="#f5f2e8"/>`);
  parts.push(`<ellipse cx="${cx}" cy="${cy - 40}" rx="120" ry="34" fill="#e6e0cf"/>`);
  parts.push(`<ellipse cx="${cx}" cy="${cy - 38}" rx="104" ry="27" fill="${color}"/>`);
  parts.push("</svg>");
  return parts.join("");
}

function setSvg(item) {
  return rollsSvg(item, 12, false);
}

for (const item of items) {
  let svg;
  if (item.category === "sets") svg = setSvg(item);
  else if (item.category === "rolls") svg = rollsSvg(item, 6, false);
  else if (item.category === "tempura") svg = rollsSvg(item, 6, true);
  else if (item.category === "sushi") svg = gunkanSvg(item);
  else if (item.category === "burgers")
    svg = /шаурма/i.test(item.name) ? shaurmaSvg(item) : burgerSvg(item);
  else if (item.category === "snacks") svg = snackSvg(item);
  else svg = extraSvg(item);
  writeFileSync(join(outDir, `${item.id}.svg`), svg);
}

console.log(`Сгенерировано картинок: ${items.length}`);
