# Docker pour Staelle Market

Docker lance trois services :

- `frontend` : Angular compilé et servi par Nginx non-root ;
- `backend` : API FastAPI/Uvicorn ;
- `db` : MariaDB avec volume persistant.

## Lancer

```bash
docker compose up --build
```

Puis ouvrir :

- boutique : http://localhost:8080
- santé API : http://localhost:8000/api/v1/health

## Secrets

Les secrets locaux sont dans `secrets/*.txt`. Ils sont ignorés par Git.

Pour régénérer des valeurs locales sous PowerShell :

```powershell
New-Guid | Set-Content secrets\db_password.txt
New-Guid | Set-Content secrets\db_root_password.txt
New-Guid | Set-Content secrets\jwt_secret.txt
New-Guid | Set-Content secrets\admin_api_key.txt
```

Avant production, remplace ces valeurs par de vrais secrets longs et uniques.

## Configuration optionnelle

Copie `.env.docker.example` vers `.env.docker` si tu veux changer les ports ou le nom de base :

```bash
docker compose --env-file .env.docker up --build
```

## Bonnes pratiques appliquées

- builds multi-stage pour réduire la taille et la surface d’attaque ;
- backend et frontend lancés sans utilisateur root ;
- secrets montés en fichiers dans `/run/secrets/...` ;
- healthchecks sur MariaDB, FastAPI et Nginx ;
- `read_only`, `cap_drop: ALL` et `no-new-privileges` sur les conteneurs applicatifs ;
- URL API relative `/api/v1`, proxyfiée en local par Angular et en Docker par Nginx.
