# Staelle Market — Angular

Catalogue e-commerce Angular avec recherche, filtres, galeries produit, stock visible, commande WhatsApp et points de retrait Google Maps.

## Lancer le projet

```bash
npm install
npm start
```

Ouvrir ensuite [http://localhost:4200](http://localhost:4200).

## Guide rapide pour débuter

Les parties importantes sont séparées pour éviter de tout modifier au même endroit :

- `src/app/store.config.ts` : numéro WhatsApp, devise et langue ;
- `src/app/products.ts` : noms, prix, stocks et informations des produits ;
- `src/app/product-images.ts` : chemins des images produit ;
- `src/app/pickup-points/pickup-points.ts` : lieux de retrait ;
- `src/app/review-form/` : formulaire d’avis ;
- `src/app/account/` : création de compte, connexion et solde de points ;
- `backend/` : API FastAPI, base de données et logique de fidélité ;
- `src/app/app.component.html` : ordre des grandes sections de la page.

Les commentaires expliquent surtout les traitements moins évidents. Les noms des variables et des méthodes décrivent le reste afin de ne pas noyer le code sous des commentaires répétitifs.

## Architecture des données

- `src/app/products.ts` contient le catalogue de secours utilisé tant que le backend n’est pas activé.
- `src/app/catalog.service.ts` est l’unique point d’accès au catalogue pour l’interface.
- `src/app/api.config.ts` configure le futur endpoint FastAPI.
- `src/app/product-images.ts` centralise les chemins et références des images.

Pour connecter FastAPI, exposer `GET /api/v1/products`, puis passer `enabled` à `true` dans `src/app/api.config.ts`. Le format attendu est documenté dans `docs/fastapi-integration.md`.

## Points de retrait

Les lieux et leurs requêtes Google Maps sont définis dans `src/app/pickup-points/pickup-points.ts` :

- Accueil de Référence Pressing à Lonkak ;
- École publique de Nkolmesseng ;
- entrée principale de la BEAC à Yaoundé.

Les cartes utilisent l’intégration Google Maps sans clé API et les boutons ouvrent l’itinéraire dans Google Maps.

## Configurer WhatsApp

Dans `src/app/store.config.ts`, remplacer le numéro de démonstration par le numéro réel, au format international sans le `+` :

```ts
whatsappNumber: "237690000000";
```

Ce numéro est utilisé pour les commandes et pour l’envoi du formulaire d’avis.

## Production

```bash
npm run build
```

La version de production est générée dans `dist/staelle-market/browser`.

Le lancement et la configuration du backend sont expliqués dans `backend/README.md`.
