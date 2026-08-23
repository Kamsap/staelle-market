# Contrat d’intégration FastAPI

L’interface Angular dépend uniquement de `CatalogService`. Le catalogue local reste actif tant que `API_CONFIG.enabled` vaut `false`.

## Endpoint attendu

```http
GET /api/v1/products
```

Deux formes de réponse sont acceptées :

```json
[
  {
    "id": 1,
    "name": "Sac à dos Essentials Back to Campus",
    "brand": "Adidas",
    "category": "Sac",
    "price": 20000,
    "stock": 2,
    "color": "Wonder Cargo / Noir",
    "description": "Sélection authentique Adidas.",
    "image": "/images/products/adidas/ke5659.jpg",
    "images": [
      "/images/products/adidas/ke5659.jpg",
      "/images/products/adidas/ke5659-2.jpg",
      "/images/products/adidas/ke5659-3.jpg"
    ],
    "featured": true
  }
]
```

ou une enveloppe paginable :

```json
{ "items": [] }
```

## Règles de données

- `price` est un entier en FCFA, déjà calculé par le backend.
- `stock` est un entier positif ou nul.
- `brand` accepte actuellement `Nike`, `Adidas` ou `Autre`.
- `category` accepte `Sac`, `Chaussure`, `Vêtement` ou `Accessoire`.
- `images` contient au moins une URL ; `image` correspond à la vue principale.
- `size`, `color` et `featured` sont optionnels.
- Le prix d’achat fournisseur et les références de commande sont des données internes : FastAPI ne doit jamais les retourner au navigateur.

## Exemple FastAPI minimal

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")

class ProductOut(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: int
    stock: int
    size: str | None = None
    color: str | None = None
    description: str
    image: str
    images: list[str]
    featured: bool | None = None

@router.get("/products", response_model=list[ProductOut])
def list_products() -> list[ProductOut]:
    return []
```

Si Angular et FastAPI utilisent des domaines différents, autoriser explicitement l’origine du frontend avec `CORSMiddleware`. Pour la production, la solution recommandée est un reverse proxy qui sert Angular et `/api/v1` sous le même domaine.
