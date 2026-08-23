import os
from io import BytesIO
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

os.environ["DATABASE_URL"] = f"sqlite:///{(BACKEND_DIR / 'test_staelle.db').as_posix()}"
os.environ["JWT_SECRET"] = "test-secret-with-more-than-thirty-two-characters"
os.environ["ADMIN_API_KEY"] = "test-admin-key"
os.environ["UPLOAD_DIR"] = str(BACKEND_DIR / "test_uploads")

from fastapi.testclient import TestClient
from PIL import Image

from app.catalog_seed import seed_catalog
from app.database import Base, SessionLocal, engine
from app.main import app


client = TestClient(app)


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        assert seed_catalog(db) == 60


def test_public_catalog_is_loaded_from_database() -> None:
    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert len(response.json()) == 60
    assert response.json()[0]["price"] == 23000
    assert len(response.json()[0]["images"]) == 3


def test_guest_and_customer_loyalty_flow() -> None:
    guest_order = client.post(
        "/api/v1/orders",
        json={"reference": "SM-GUEST-123456", "product_id": 1},
    )
    assert guest_order.status_code == 201
    assert guest_order.json()["customer_id"] is None
    assert guest_order.json()["displayed_price"] == 23000

    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Cliente Test",
            "email": "cliente@example.com",
            "phone": "690000000",
            "password": "motdepasse123",
        },
    )
    assert register.status_code == 201
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={"reference": "SM-CLIENT-123456", "product_id": 2},
    )
    assert order.status_code == 201

    confirmed = client.post(
        f"/api/v1/orders/{order.json()['id']}/confirm",
        headers={"X-Admin-Key": "test-admin-key"},
        json={"amount_paid": 20000},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["points_earned"] == 20

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.json()["points"] == 20

    products = client.get("/api/v1/products").json()
    assert products[1]["stock"] == 1


def test_admin_catalog_and_stock_flow() -> None:
    anonymous = TestClient(app)
    assert anonymous.get("/api/v1/admin/products").status_code == 401
    assert (
        anonymous.post(
            "/api/v1/admin/auth/login",
            headers={"Origin": "https://attacker.example"},
            json={"email": "admin@example.com", "password": "invalid"},
        ).status_code
        == 403
    )

    bootstrap = client.post(
        "/api/v1/admin/auth/bootstrap",
        headers={"X-Admin-Key": "test-admin-key"},
        json={
            "full_name": "Responsable Boutique",
            "email": "admin@example.com",
            "password": "un-mot-de-passe-solide",
        },
    )
    assert bootstrap.status_code == 201

    admin_client = TestClient(app)
    login = admin_client.post(
        "/api/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "un-mot-de-passe-solide"},
    )
    assert login.status_code == 200
    assert login.cookies.get("staelle_admin_session")

    dashboard = admin_client.get("/api/v1/admin/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["active_products"] == 60

    payload = {
        "name": "Sac test administration",
        "slug": "sac-test-administration",
        "brand": "Staelle",
        "category": "Sac",
        "description": "Article utilisé pour vérifier le parcours administrateur.",
        "status": "active",
        "featured": False,
        "variants": [
            {
                "sku": "STA-TEST-001",
                "size": None,
                "color": "Noir",
                "selling_price": 12500,
                "cost_price": 8000,
                "stock_on_hand": 4,
                "stock_reserved": 0,
                "low_stock_threshold": 1,
                "is_active": True,
            }
        ],
        "images": [
            {
                "path": "/images/products/adidas/ke5659.jpg",
                "alt_text": "Sac test administration",
                "position": 0,
            }
        ],
    }
    created = admin_client.post("/api/v1/admin/products", json=payload)
    assert created.status_code == 201, created.text
    product = created.json()
    assert product["variants"][0]["available_stock"] == 4

    payload["variants"][0]["id"] = product["variants"][0]["id"]
    payload["variants"][0]["selling_price"] = 13000
    updated = admin_client.put(f"/api/v1/admin/products/{product['id']}", json=payload)
    assert updated.status_code == 200, updated.text
    assert updated.json()["variants"][0]["selling_price"] == 13000

    movement = admin_client.post(
        "/api/v1/admin/stock-adjustments",
        json={
            "variant_id": product["variants"][0]["id"],
            "quantity_delta": 3,
            "kind": "receipt",
            "note": "Réception du fournisseur",
        },
    )
    assert movement.status_code == 200, movement.text
    assert movement.json()["stock_after"] == 7

    image_bytes = BytesIO()
    Image.new("RGB", (40, 50), "#bdff22").save(image_bytes, format="PNG")
    uploaded = admin_client.post(
        "/api/v1/admin/uploads",
        files={"file": ("article.png", image_bytes.getvalue(), "image/png")},
    )
    assert uploaded.status_code == 201, uploaded.text
    assert uploaded.json()["url"].startswith("/api/v1/media/")

    public_product = client.get(f"/api/v1/products/{product['id']}")
    assert public_product.status_code == 200
    assert public_product.json()["price"] == 13000
    assert public_product.json()["stock"] == 7

    archived = admin_client.delete(f"/api/v1/admin/products/{product['id']}")
    assert archived.status_code == 204
    assert client.get(f"/api/v1/products/{product['id']}").status_code == 404
