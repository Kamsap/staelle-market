export type ProductStatus = 'Disponible' | 'Stock limité' | 'Rupture';
export interface Product { id:number; name:string; brand:'Nike'|'Adidas'|'Autre'; category:'Sac'|'Chaussure'|'Vêtement'|'Accessoire'; price:number; stock:number; size?:string; color?:string; description:string; image:string; featured?:boolean; }
export const PRODUCTS: Product[] = [
  { id:1,name:'Sac à dos Nike Sport',brand:'Nike',category:'Sac',price:18000,stock:4,color:'Noir',description:'Sac sport et lifestyle pour le quotidien.',image:'/images/product-nike-bag.svg',featured:true },
  { id:2,name:'Sac Adidas Classic',brand:'Adidas',category:'Sac',price:16000,stock:2,color:'Bleu marine',description:'Format léger et polyvalent.',image:'/images/product-adidas-bag.svg',featured:true },
  { id:3,name:'Casquette sport premium',brand:'Autre',category:'Accessoire',price:7000,stock:8,color:'Beige',description:'Une finition nette pour tous les looks.',image:'/images/product-cap.svg' },
  { id:4,name:'T-shirt training',brand:'Nike',category:'Vêtement',price:12000,stock:0,size:'M / L',color:'Blanc',description:'Confort technique, allure décontractée.',image:'/images/product-shirt.svg' }
];
