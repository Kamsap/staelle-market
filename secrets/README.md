# Secrets Docker locaux

Ce dossier sert uniquement aux secrets locaux utilisés par `docker compose`.

À créer avant le premier lancement :

```powershell
New-Guid | Set-Content secrets\db_password.txt
New-Guid | Set-Content secrets\db_root_password.txt
New-Guid | Set-Content secrets\jwt_secret.txt
New-Guid | Set-Content secrets\admin_api_key.txt
```

Ces fichiers sont ignorés par Git. Ne les pousse jamais sur GitHub.
