from fastapi.testclient import TestClient
from app.main import app
from app.models import Wallet
from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import status

client = TestClient(app)

def test_create_wallet():
    response = client.post("/wallet/", json={"balance": 100.0})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["balance"] == 100.0

def test_get_wallet():
    response = client.get("/wallet/1/")
    assert response.status_code == status.HTTP_200_OK
    assert "balance" in response.json()

def test_update_wallet():
    response = client.put("/wallet/1/", json={"balance": 150.0})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["balance"] == 150.0

def test_delete_wallet():
    response = client.delete("/wallet/1/")
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_get_nonexistent_wallet():
    response = client.get("/wallet/999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND