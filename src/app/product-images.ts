export interface ProductImageSource {
  path: string;
  paths: string[];
  reference: string;
  source: 'adidas.com' | 'showroomprive.com' | 'nike.com';
}

const adidas = (reference: string): ProductImageSource => ({
  path: `/images/products/adidas/${reference.toLowerCase()}.jpg`,
  paths: [
    `/images/products/adidas/${reference.toLowerCase()}.jpg`,
    `/images/products/adidas/${reference.toLowerCase()}-2.jpg`,
    `/images/products/adidas/${reference.toLowerCase()}-3.jpg`
  ],
  reference,
  source: 'adidas.com'
});

const showroom = (reference: string): ProductImageSource => ({
  path: `/images/products/showroomprive/${reference}.jpg`,
  paths: reference === '40491277'
    ? [`/images/products/showroomprive/${reference}.jpg`]
    : reference === '40319142'
      ? [
          `/images/products/showroomprive/${reference}.jpg`,
          `/images/products/showroomprive/${reference}-3.jpg`
        ]
    : [
        `/images/products/showroomprive/${reference}.jpg`,
        `/images/products/showroomprive/${reference}-2.jpg`,
        `/images/products/showroomprive/${reference}-3.jpg`
      ],
  reference,
  source: 'showroomprive.com'
});

const nike = (reference: string): ProductImageSource => ({
  path: `/images/products/nike/${reference.toLowerCase()}.avif`,
  paths: [
    `/images/products/nike/${reference.toLowerCase()}.avif`,
    `/images/products/nike/${reference.toLowerCase()}-2.avif`,
    `/images/products/nike/${reference.toLowerCase()}-3.avif`
  ],
  reference,
  source: 'nike.com'
});

export const PRODUCT_IMAGE_SOURCES: Record<number, ProductImageSource> = {
  1: adidas('KE5659'), 2: adidas('KC6820'), 3: adidas('KH1560'),
  4: adidas('IY1816'), 5: adidas('JW0314'), 6: adidas('KE3780'),
  7: adidas('JX0213'), 8: adidas('JW1465'), 9: adidas('JH8847'),
  10: adidas('KC8894'), 11: adidas('KT2255'), 12: adidas('KE0110'),
  13: adidas('KC6822'), 14: adidas('JY7644'), 15: adidas('HK2625'),
  16: adidas('JX0215'), 17: adidas('KD7845'), 18: adidas('KD7844'),
  19: adidas('KC8648'), 20: adidas('IM5523'), 21: adidas('IY9404'),
  22: adidas('KE5637'), 23: adidas('KC9922'), 24: adidas('JX0253'),
  25: adidas('KD7848'), 26: adidas('IU0009'), 27: adidas('JM9059'),
  28: adidas('JP7443'), 29: adidas('KE0412'),

  30: showroom('40302477'), 31: showroom('40319056'), 32: showroom('40319093'),
  33: showroom('40319125'), 34: showroom('40319146'), 35: showroom('40319154'),
  36: showroom('40319158'), 37: showroom('40319592'), 38: showroom('40319142'),
  39: showroom('40319153'), 40: showroom('40491223'), 41: showroom('40319159'),
  42: showroom('40319167'), 43: showroom('40319160'), 44: showroom('40302534'),
  45: showroom('40302568'), 46: showroom('40302659'), 47: showroom('40302799'),
  48: showroom('40302858'), 49: showroom('40302859'), 50: showroom('40491277'),
  51: showroom('40302990'), 52: showroom('40319514'), 53: showroom('40319148'),

  54: nike('DD0562-323'), 55: nike('BA6032-009'), 56: nike('DR6100-634'),
  57: nike('DM3976-010'), 58: nike('DC4244-364'), 59: nike('DD0559-017'),
  60: nike('DR6100-480')
};
