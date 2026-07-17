# Backend Staelle Market

Ce backend gère les comptes clients, les commandes invitées et clientes, ainsi que les points de fidélité.

## Lancer en local sous Windows

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

L’API est ensuite disponible sur `http://127.0.0.1:8000` et sa documentation sur `http://127.0.0.1:8000/docs`.

## Règles de fidélité

- une commande peut appartenir à un client ou rester invitée ;
- une commande nouvellement créée reste `pending` ;
- les points sont crédités uniquement après confirmation administrative ;
- le réglage par défaut donne 1 point par tranche de 1 000 FCFA payés ;
- une commande invitée ne rapporte pas de points.

Pour confirmer une commande :

```http
POST /api/v1/orders/{order_id}/confirm
X-Admin-Key: valeur-de-ADMIN_API_KEY

{"amount_paid": 20000}
```

## Production

Avant tout déploiement :

1. définir des valeurs longues et uniques pour `JWT_SECRET` et `ADMIN_API_KEY` ;
2. remplacer `DATABASE_URL` par la connexion MariaDB fournie par l’hébergeur ;
3. limiter `FRONTEND_ORIGINS` au vrai domaine ;
4. remplacer l’URL locale dans `src/app/api.config.ts` par `/api/v1` si le frontend et l’API partagent le même domaine.

Le MVP crée automatiquement les tables. Avant les premières évolutions en production, il faudra ajouter Alembic pour versionner les migrations de base de données.
