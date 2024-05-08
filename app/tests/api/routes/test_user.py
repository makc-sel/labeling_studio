from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.routes.exception import *


def test_valid_create_user(
        client: TestClient,
        db:Session
):
        response = client.post(
                "/user/",
                json={"username":"test","email":"test@email.com","hashed_password":"pass"}
        )
        assert response.status_code==200

def test_invalid_create_user_bad_email(db:Session, client: TestClient):
        response = client.post(
                "/user/",
                json={"username":"test","email":"test@email.com","hashed_password":"pass"}
        )
        assert response.status_code==200
        
        response = client.post(
                "/user/",
                json={"username":"test2","email":"test@email.com","hashed_password":"pass"}
        )
        assert response.status_code==400
        assert response.json()["detail"] == UserExistedException.detail

def test_invalid_create_user_bad_username(db:Session, client: TestClient):
        response = client.post(
                "/user/",
                json={"username":"test","email":"test@email.com","hashed_password":"pass"}
        )
        assert response.status_code==200
        
        response = client.post(
                "/user/",
                json={"username":"test","email":"test2@email.com","hashed_password":"pass"}
        )
        assert response.status_code==400
        assert response.json()["detail"] == UserExistedException.detail
