
import database
from fastapi.testclient import TestClient
from main import app


def setup_test_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test_giveconnect.db"

    monkeypatch.setattr(database, "DATABASE_NAME", str(test_db))
    database.initialize_database()


def test_home_page():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "GiveConnect" in response.text


def test_donor_page(tmp_path, monkeypatch):
    setup_test_database(tmp_path, monkeypatch)

    client = TestClient(app)
    response = client.get("/donor")

    assert response.status_code == 200
    assert "Your Donations" in response.text


def test_beneficiary_page(tmp_path, monkeypatch):
    setup_test_database(tmp_path, monkeypatch)

    client = TestClient(app)
    response = client.get("/beneficiary")

    assert response.status_code == 200
    assert "Available Donations" in response.text


def test_create_donation(tmp_path, monkeypatch):
    setup_test_database(tmp_path, monkeypatch)

    client = TestClient(app)

    response = client.post(
        "/donate",
        data={
            "title": "Winter Jacket",
            "description": "A warm winter jacket",
            "category": "Clothing",
            "donor_name": "Test Donor"
        },
        follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/donor"

    donations = client.get("/check-donations").json()

    assert len(donations) == 1
    assert donations[0]["title"] == "Winter Jacket"
    assert donations[0]["donor_name"] == "Test Donor"
    assert donations[0]["status"] == "available"
