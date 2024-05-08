from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.tests.utils.species import create_test_species


def test_valid_create_species(client: TestClient,db:Session):
        response = client.post(
                "/species/",
                json={"name":"species"}
        )
        assert response.status_code==200
        assert response.json()["id"] == 1
        assert response.json()["name"] == "species"

def test_invalid_create_species(client: TestClient, db:Session):
        species = create_test_species(db=db)
        response = client.post(
                "/species/",
                json={
                        "name":species.name
                }
        )
        assert response.status_code==400

def test_valid_get_species_by_id(client:TestClient, db:Session):
        species = create_test_species(db=db)
        response = client.get(f"/species/{species.id}")
        assert response.status_code == 200
        assert response.json()["id"] == species.id
        assert response.json()["name"] == species.name

def test_invalid_get_species_by_id(client:TestClient, db:Session):
        response = client.get(f"/species/{1}")
        assert response.status_code == 404