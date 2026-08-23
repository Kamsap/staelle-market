# Staelle Market — Angular

Boutique e-commerce Angular avec catalogue administrable, galeries produit, commande WhatsApp, comptes clients, fidélité et points de retrait.

## Lancer le projet

```bash
npm install
npm start
```

Ouvrir ensuite [http://localhost:4200](http://localhost:4200). Le backend doit également être lancé comme indiqué dans `backend/README.md`.

## Repères pour débuter

- `src/app/store.config.ts` : numéro WhatsApp, devise et langue ;
- `src/app/products.ts` : catalogue de secours si l’API est indisponible ;
- `src/app/product-images.ts` : chemins des images historiques ;
- `src/app/catalog.service.ts` : accès unique au catalogue de l’API ;
- `src/app/admin/` : interface de gestion accessible à l’adresse `/admin` ;
- `src/app/pickup-points/` : lieux de retrait ;
- `src/app/review-form/` : formulaire d’avis ;
- `src/app/account/` : compte client et points ;
- `backend/` : API FastAPI, MariaDB, sécurité et logique métier.

## Catalogue et administration

MariaDB est la source principale des articles, prix, variantes, images et stocks. Les changements effectués dans `/admin` sont visibles dans la boutique sans modifier le code Angular.

L’administration permet de :

- ajouter, modifier, publier ou archiver un article ;
- gérer prix final, prix d’achat, SKU, tailles et couleurs ;
- ajouter jusqu’à dix photos contrôlées côté serveur ;
- enregistrer les réceptions, retours, ventes manuelles et corrections de stock ;
- suivre les indicateurs principaux du catalogue.

Le premier compte administrateur est créé une seule fois avec l’endpoint protégé `POST /api/v1/admin/auth/bootstrap`. La procédure est dans `backend/README.md`.

## Points de retrait

Les lieux sont définis dans `src/app/pickup-points/pickup-points.ts` :

- accueil de Référence Pressing à Lonkak ;
- École publique de Nkolmesseng ;
- entrée principale de la BEAC à Yaoundé.

## WhatsApp

Le numéro au format international sans `+` se trouve dans `src/app/store.config.ts`. Il est utilisé pour les commandes et les avis.

## Production

```bash
npm run build
```

La version de production est générée dans `dist/staelle-market/browser`. La procédure O2switch se trouve dans `DEPLOIEMENT-O2SWITCH.md`.
