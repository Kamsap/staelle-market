import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const productSource = await readFile(resolve(root, "src/app/products.ts"), "utf8");
const imageSource = await readFile(resolve(root, "src/app/product-images.ts"), "utf8");

const imageReferences = new Map();
for (const match of imageSource.matchAll(/(\d+):\s*(adidas|showroom|nike)\('([^']+)'\)/g)) {
  imageReferences.set(Number(match[1]), { provider: match[2], reference: match[3] });
}

const slugify = (value) =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const pathsFor = ({ provider, reference }) => {
  if (provider === "adidas") {
    const base = `/images/products/adidas/${reference.toLowerCase()}`;
    return [`${base}.jpg`, `${base}-2.jpg`, `${base}-3.jpg`];
  }
  if (provider === "nike") {
    const base = `/images/products/nike/${reference.toLowerCase()}`;
    return [`${base}.avif`, `${base}-2.avif`, `${base}-3.avif`];
  }
  const base = `/images/products/showroomprive/${reference}`;
  if (reference === "40491277") return [`${base}.jpg`];
  if (reference === "40319142") return [`${base}.jpg`, `${base}-3.jpg`];
  return [`${base}.jpg`, `${base}-2.jpg`, `${base}-3.jpg`];
};

const products = [];
for (const match of productSource.matchAll(/product\(\{([^\r\n]+)\}\)/g)) {
  // Le fichier appartient au projet : l'objet est évalué uniquement pendant la génération locale.
  const seed = Function(`"use strict"; return ({${match[1]}});`)();
  const imageReference = imageReferences.get(seed.id);
  if (!imageReference) throw new Error(`Images introuvables pour l'article ${seed.id}`);
  const images = pathsFor(imageReference);
  products.push({
    id: seed.id,
    name: seed.name,
    slug: `${slugify(seed.name)}-${seed.id}`,
    brand: seed.brand,
    category: seed.category,
    description: `${seed.name}${seed.color ? ` en ${seed.color.toLowerCase()}` : ""}. Sélection authentique ${seed.brand}.`,
    status: "active",
    featured: Boolean(seed.featured),
    variants: [
      {
        sku: imageReference.reference,
        size: seed.size ?? null,
        color: seed.color ?? null,
        selling_price: Math.round(seed.price * 1.15),
        compare_at_price: null,
        cost_price: null,
        stock_on_hand: seed.stock,
        stock_reserved: 0,
        low_stock_threshold: 2,
        is_active: true,
      },
    ],
    images: images.map((path, position) => ({
      path,
      alt_text: seed.name,
      position,
    })),
  });
}

if (products.length !== 60) {
  throw new Error(`60 articles attendus, ${products.length} trouvés`);
}

await writeFile(
  resolve(root, "backend/app/catalog_seed.json"),
  `${JSON.stringify(products, null, 2)}\n`,
  "utf8",
);
console.log(`${products.length} articles exportés vers backend/app/catalog_seed.json`);
