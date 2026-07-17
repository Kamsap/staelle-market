import { PRODUCT_IMAGE_SOURCES } from './product-images';

export type ProductStatus = 'Disponible' | 'Stock limité' | 'Rupture';

export interface Product {
  id: number;
  name: string;
  brand: 'Nike' | 'Adidas' | 'Autre';
  category: 'Sac' | 'Chaussure' | 'Vêtement' | 'Accessoire';
  price: number;
  stock: number;
  size?: string;
  color?: string;
  description: string;
  image: string;
  images: string[];
  featured?: boolean;
}


type ProductSeed = Omit<Product, 'description' | 'image' | 'images'> & { image?: string; images?: string[] };

const imageFor = (product: ProductSeed): string => {
  if (product.category === 'Chaussure') return '/images/product-shoe.svg';
  if (product.category === 'Vêtement') return '/images/product-shirt.svg';
  if (product.category === 'Accessoire') return '/images/product-cap.svg';
  return product.brand === 'Nike' ? '/images/product-nike-bag.svg' : '/images/product-adidas-bag.svg';
};

const product = (seed: ProductSeed): Product => {
  const image = seed.image ?? PRODUCT_IMAGE_SOURCES[seed.id]?.path ?? imageFor(seed);
  return {
    ...seed,
    description: `${seed.name}${seed.color ? ` en ${seed.color.toLowerCase()}` : ''}. Sélection authentique ${seed.brand}.`,
    image,
    images: seed.images ?? PRODUCT_IMAGE_SOURCES[seed.id]?.paths ?? [image]
  };
};

export const PRODUCTS: Product[] = [
  // adidas.com — stock importé en juillet 2026
  product({ id: 1, name: 'Sac à dos Essentials Back to Campus', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Wonder Cargo / Noir', price: 20000, featured: true }),
  product({ id: 2, name: 'Tote Bag Adidas Prime', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Halo Silver', price: 20000 }),
  product({ id: 3, name: 'Sac à dos Classic Tape Lamine Yamal', brand: 'Adidas', category: 'Sac', stock: 4, color: 'Blanc / Rouge', price: 20500, featured: true }),
  product({ id: 4, name: 'Sac en toile 4ATHLTS petit format', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Bleu marine / Blanc', price: 21500 }),
  product({ id: 5, name: 'Sac à dos avec trousse', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Bleu', price: 23500 }),
  product({ id: 6, name: 'Sac à dos Adidas Primelift', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Lavande / Bleu marine', price: 27000 }),
  product({ id: 7, name: 'Sac à dos Adicolor Classic', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Night Indigo', price: 18500 }),
  product({ id: 8, name: 'Sac à dos All Blacks', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Noir', price: 29000 }),
  product({ id: 9, name: 'Predator Club multi-surfaces', brand: 'Adidas', category: 'Chaussure', stock: 1, size: '42', color: 'Blanc / Noir / Jaune', price: 33500 }),
  product({ id: 10, name: 'Sac à dos Predator Training Power', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Blanc / Noir / Rouge', price: 34000 }),
  product({ id: 11, name: 'Sac à dos Tiro Junior', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Rose / Blanc', price: 37000 }),
  product({ id: 12, name: 'Sac à cordon Everyday Icons', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Kaki', price: 25000 }),
  product({ id: 13, name: 'Sac à dos Adidas Prime', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Wonder Sage', price: 27000 }),
  product({ id: 14, name: 'Sac à dos Adidas Prime', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Halo Silver', price: 25000 }),
  product({ id: 15, name: 'Sac à dos Adicolor', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Bliss Pink', price: 18500 }),
  product({ id: 16, name: 'Sac à dos Adicolor Classic', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Better Scarlet', price: 20500 }),
  product({ id: 17, name: 'Sac Adicolor XS', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Night Indigo', price: 28000 }),
  product({ id: 18, name: 'Sac Adicolor XS', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Aurora Coffee', price: 30500 }),
  product({ id: 19, name: 'Sac à dos effet délavé CL', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Noir', price: 31000 }),
  product({ id: 20, name: 'Sac en toile 4ATHLTS petit format', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Noir / Blanc', price: 23500 }),
  product({ id: 21, name: 'Sac à dos APWR', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Bleu marine multicolore', price: 21500 }),
  product({ id: 22, name: 'Sac à dos 3 bandes Back-to-School', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Tropic Bloom / Blanc', price: 17500 }),
  product({ id: 23, name: 'Sac de sport Training Defender M', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Noir / Beige', price: 28000 }),
  product({ id: 24, name: 'Sac Airliner', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Blanc', price: 34000 }),
  product({ id: 25, name: 'Sac Airliner Adicolor', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Blanc / Crystal Sky', price: 30500 }),
  product({ id: 26, name: 'Sac à dos monogramme', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Noir', price: 25500 }),
  product({ id: 27, name: 'Sac Essentials 3-Stripes moyen', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Bleu foncé / Blanc', price: 22500 }),
  product({ id: 28, name: 'F50 Messi Club multi-surfaces', brand: 'Adidas', category: 'Chaussure', stock: 1, size: '41 1/3', color: 'Blanc / Rouge / Argent', price: 40000, featured: true }),
  product({ id: 29, name: 'Sac à dos Logo Enfants', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Bleu / Blanc', price: 17000 }),

  // Showroomprivé — stock Adidas importé en juillet 2026
  product({ id: 30, name: 'Sac à dos de basketball', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Blanc', price: 20000 }),
  product({ id: 31, name: 'Sac de football Tiro League', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Rouge', price: 16000 }),
  product({ id: 32, name: 'Sac bowling', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Noir', price: 14500 }),
  product({ id: 33, name: 'Sac à dos Lin G', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Rose', price: 17000 }),
  product({ id: 34, name: 'Sac porté épaule Liberty', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Blanc / Jaune', price: 31500 }),
  product({ id: 35, name: 'Sac à dos Classic', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Rose', price: 14500 }),
  product({ id: 36, name: 'Sac à dos d’entraînement', brand: 'Adidas', category: 'Sac', stock: 1, color: 'Rose', price: 17000 }),
  product({ id: 37, name: 'Sac à dos Doodle', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Rose', price: 11500 }),
  product({ id: 38, name: 'Sac à dos Adicolor Classic', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Marron', price: 18500 }),
  product({ id: 39, name: 'Sac à dos Essentials', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Bleu marine', price: 11000 }),
  product({ id: 40, name: 'Sac à dos Classic', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Bleu ciel', price: 13500 }),
  product({ id: 41, name: 'Sac à dos Training Bars', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Marron', price: 11500 }),
  product({ id: 42, name: 'Sac à dos Linear Colorblock', brand: 'Adidas', category: 'Sac', stock: 4, color: 'Bleu', price: 10000, featured: true }),
  product({ id: 43, name: 'Sac à dos Training Bars', brand: 'Adidas', category: 'Sac', stock: 2, color: 'Gris clair', price: 11500 }),
  product({ id: 44, name: 'Baskets Tensaur', brand: 'Adidas', category: 'Chaussure', stock: 1, size: '20', color: 'Bleu marine', price: 16000 }),
  product({ id: 45, name: 'Chaussures de football Lionel Messi', brand: 'Adidas', category: 'Chaussure', stock: 1, size: '45 1/3', color: 'Blanc', price: 41500 }),
  product({ id: 46, name: 'Pantalon loose Wardrobe Essentials', brand: 'Adidas', category: 'Vêtement', stock: 1, size: 'L', color: 'Gris clair chiné', price: 21500 }),
  product({ id: 47, name: 'Veste Adidas bicolore', brand: 'Adidas', category: 'Vêtement', stock: 1, size: 'M', color: 'Noir / Blanc', price: 22500 }),
  product({ id: 48, name: 'Veste de survêtement Main Originals', brand: 'Adidas', category: 'Vêtement', stock: 2, size: '15/16 ans', color: 'Noir', price: 18000 }),
  product({ id: 49, name: 'Veste House of Tiro', brand: 'Adidas', category: 'Vêtement', stock: 1, size: 'M', color: 'Vert d’eau', price: 31500 }),
  product({ id: 50, name: 'Lot de 3 paires de chaussettes', brand: 'Adidas', category: 'Accessoire', stock: 2, size: '22/24', color: 'Blanc / Rouge / Vert', price: 3500 }),
  product({ id: 51, name: 'T-shirt Training Essentials', brand: 'Adidas', category: 'Vêtement', stock: 2, size: '15/16 ans', color: 'Vert d’eau', price: 6000 }),
  product({ id: 52, name: 'T-shirt Training Sere', brand: 'Adidas', category: 'Vêtement', stock: 2, size: '15/16 ans', color: 'Blanc', price: 11500 }),
  product({ id: 53, name: 'Lot de 2 paires de chaussettes Ruffle', brand: 'Adidas', category: 'Accessoire', stock: 2, size: '40/42', color: 'Blanc', price: 6500 }),

  // Nike — stock importé en juillet 2026
  product({ id: 54, name: 'Sac à dos Nike 21 L — DD0562-323', brand: 'Nike', category: 'Sac', stock: 1, color: 'Vert', price: 30500, featured: true }),
  product({ id: 55, name: 'Sac à dos enfant Nike 20 L — BA6032-009', brand: 'Nike', category: 'Sac', stock: 2, color: 'Noir', price: 26500 }),
  product({ id: 56, name: 'Sac enfant Nike Gym Club 25 L — DR6100-634', brand: 'Nike', category: 'Sac', stock: 2, color: 'Rose', price: 26500 }),
  product({ id: 57, name: 'Sac de sport Nike Brasilia 41 L — DM3976-010', brand: 'Nike', category: 'Sac', stock: 1, color: 'Noir', price: 30500 }),
  product({ id: 58, name: 'Sac à dos Nike Heritage 25 L — DC4244-364', brand: 'Nike', category: 'Sac', stock: 2, color: 'Vert', price: 27500, featured: true }),
  product({ id: 59, name: 'Sac à dos Nike 21 L — DD0559-017', brand: 'Nike', category: 'Sac', stock: 1, color: 'Noir', price: 30500 }),
  product({ id: 60, name: 'Sac enfant Nike Gym Club 25 L — DR6100-480', brand: 'Nike', category: 'Sac', stock: 1, color: 'Bleu', price: 26500 })
];
