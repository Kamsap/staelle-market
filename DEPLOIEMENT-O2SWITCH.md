# Déploiement O2switch — Staelle Market

## Architecture recommandée

- Front Angular : fichiers statiques dans le dossier du domaine, souvent `public_html` ou `ton-domaine.tld`.
- Backend FastAPI : application Python séparée, hors du dossier public.
- Base : MySQL/MariaDB créée dans cPanel.

Cette séparation évite d’exposer le code backend si l’application Python est arrêtée.

## 1. Préparer la base MySQL

Dans cPanel :

1. ouvrir **Bases de données MySQL** ;
2. créer une base, par exemple `staelle_market` ;
3. créer un utilisateur dédié ;
4. donner les droits à cet utilisateur sur cette base.

O2switch préfixe généralement les noms avec l’identifiant cPanel, par exemple :

```txt
compte_staelle_market
compte_staelle_user
```

## 2. Déployer le backend Python

Dans cPanel > **Setup Python App** :

1. créer une application Python ;
2. choisir Python 3.11 si disponible ;
3. mettre l’application dans un dossier hors web public, par exemple `staelle-api` ;
4. mettre l’URL de l’application sur `/api` si tu veux garder l’API sur le même domaine ;
5. définir :

```txt
Application startup file : passenger_wsgi.py
Application entry point : application
```

Ensuite, depuis Terminal/SSH, entrer dans l’environnement Python donné par cPanel, puis :

```bash
cd ~/staelle-api
pip install -r requirements.txt
```

Variables à ajouter dans **Setup Python App > Add Variable** :

```txt
APP_ENV=production
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=compte_staelle_market
DATABASE_USER=compte_staelle_user
DATABASE_PASSWORD=mot_de_passe_mysql
JWT_SECRET=secret_long_unique
ADMIN_API_KEY=cle_admin_longue_unique
FRONTEND_ORIGINS=https://ton-domaine.com
POINTS_PER_XAF=1000
```

Puis redémarrer l’application Python.

## 3. Déployer le front Angular

Construire le front :

```bash
npm run build
```

Uploader le contenu de :

```txt
dist/staelle-market/browser
```

dans le dossier du domaine sur O2switch.

Le fichier `.htaccess` généré avec le build permet à Angular de fonctionner même si le client ouvre une route interne directement.

## 4. Tester

Tester l’API :

```txt
https://ton-domaine.com/api/v1/health
```

Résultat attendu :

```json
{"status":"ok"}
```

Tester ensuite :

- création de compte ;
- connexion ;
- commande invitée ;
- commande connectée ;
- confirmation admin via l’endpoint backend.

## Point important

Si O2switch ne conserve pas le préfixe `/api` dans les URLs Python, il faudra soit :

- monter l’application Python directement sur `/api` et garder `baseUrl: "/api/v1"` ;
- soit utiliser un sous-domaine `api.ton-domaine.com` et remplacer `baseUrl` dans `src/app/api.config.ts`.
