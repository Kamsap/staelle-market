# Staelle Market — Angular

Catalogue e-commerce moderne pour Staelle Market : recherche, filtres, stock visible et commande directe via WhatsApp.

## Lancer le projet en local

```bash
npm install
npm start
```

Ouvrir ensuite [http://localhost:4200](http://localhost:4200).

## Modifier les produits

Les produits sont définis dans `src/app/products.ts`. Chaque article peut préciser son nom, sa marque, sa catégorie, son prix, son stock, sa taille, sa couleur, sa description et son image.

## Configurer WhatsApp

Dans `src/app/app.component.ts`, remplace le numéro suivant par le vrai numéro au format international, sans le `+` :

```ts
readonly whatsappNumber = '237690000000';
```

## Générer la version de production

```bash
npm run build
```

Les fichiers prêts à héberger sont générés dans `dist/staelle-market/browser`.
