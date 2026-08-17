# Backend Staelle Market

Ce backend gère le catalogue, les comptes administrateurs et clients, les commandes, le stock et les points de fidélité.

## Lancer en local sous Windows

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
uvicorn app.main:app --reload
```

L’API est disponible sur `http://127.0.0.1:8000` et sa documentation sur `http://127.0.0.1:8000/docs`.

## Créer le premier administrateur

Cette opération ne fonctionne que tant qu’aucun administrateur n’existe. Utiliser la valeur `ADMIN_API_KEY` du fichier `.env` :

```powershell
$body = @{
  full_name = "Responsable boutique"
  email = "admin@example.com"
  password = "un-mot-de-passe-long-et-unique"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/v1/admin/auth/bootstrap `
  -Method Post `
  -Headers @{ "X-Admin-Key" = "VOTRE_ADMIN_API_KEY" } `
  -ContentType "application/json" `
  -Body $body
```

L’administrateur se connecte ensuite sur `/admin`. Sa session utilise un cookie `HttpOnly`, limité aux routes administratives.

## Catalogue et stock

- le prix d’une commande est relu en base : le navigateur ne peut pas imposer son prix ;
- chaque modification de stock crée un mouvement horodaté ;
- l’archivage retire l’article de la boutique sans supprimer son historique ;
- les fichiers JPG, PNG et WebP sont validés puis réencodés avant stockage ;
- `app/catalog_seed.json` importe les 60 articles uniquement si le catalogue est vide.

## Fidélité

- une commande peut appartenir à un client ou rester invitée ;
- une commande nouvellement créée reste `pending` ;
- les points sont crédités après confirmation administrative ;
- par défaut, 1 point est accordé par tranche de 1 000 FCFA payés ;
- une commande invitée ne rapporte pas de points.

## Production

Avant le redémarrage d’une nouvelle version :

```bash
python -m alembic upgrade head
```

Les valeurs `JWT_SECRET` et `ADMIN_API_KEY` doivent être longues, aléatoires et uniques. Limiter `FRONTEND_ORIGINS` au domaine réel et placer `UPLOAD_DIR` dans un dossier persistant.
