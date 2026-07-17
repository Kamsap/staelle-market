"""Point d'entrée WSGI pour cPanel / O2switch.

FastAPI est une application ASGI. O2switch exécute les applications Python avec
Passenger et WSGI : l'adaptateur a2wsgi fait le pont entre les deux mondes.

Dans "Setup Python App", configurer :
- Application startup file : passenger_wsgi.py
- Application entry point : application
"""

from a2wsgi import ASGIMiddleware

from app.main import app


application = ASGIMiddleware(app)
