"""Point d'entrée WSGI de Staelle Market pour cPanel / O2switch.

FastAPI est une application ASGI. O2switch exécute les applications Python avec
Passenger et WSGI : l'adaptateur a2wsgi fait le pont entre les deux mondes.

Dans "Setup Python App", configurer :
- Application startup file : staelle_wsgi.py
- Application entry point : application

Le nom est volontairement différent de ``passenger_wsgi.py`` : cPanel génère
lui-même ce dernier fichier et l'utilise comme lanceur interne.
"""

from a2wsgi import ASGIMiddleware

from app.main import app


application = ASGIMiddleware(app)
