import os

os.environ["DATABASE_URL"] = "sqlite:///./test_staelle.db"
os.environ["JWT_SECRET"] = "test-secret-with-more-than-thirty-two-characters"
os.environ["ADMIN_API_KEY"] = "test-admin-key"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_guest_and_customer_loyalty_flow() -> None:
    guest_order = client.post(
        "/api/v1/orders",
        json={
            "reference": "SM-GUEST-123456",
            "product_id": 1,
            "product_name": "Sac test",
            "displayed_price": 20000,
        },
    )
    assert guest_order.status_code == 201
    assert guest_order.json()["customer_id"] is None

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
        json={
            "reference": "SM-CLIENT-123456",
            "product_id": 2,
            "product_name": "Tote Bag test",
            "displayed_price": 20000,
        },
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
