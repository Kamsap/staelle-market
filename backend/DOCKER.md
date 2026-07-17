# Docker côté backend

Le backend accepte deux modes de configuration :

- `DATABASE_URL`, pratique en local avec SQLite ;
- `DATABASE_HOST`, `DATABASE_NAME`, `DATABASE_USER` et `DATABASE_PASSWORD_FILE`, recommandé avec Docker secrets.

Secrets reconnus :

- `JWT_SECRET_FILE` ;
- `ADMIN_API_KEY_FILE` ;
- `DATABASE_PASSWORD_FILE`.

Quand `APP_ENV=production`, le backend refuse de démarrer avec des secrets courts ou les valeurs de développement par défaut.
