from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.tests.utils.image import create_test_image
from app.tests.utils.user import create_test_user
from app.tests.utils.task import create_test_task
from app.core.database import TaskType, TaskStatus
from app.settings import image_domain
import os

def test_valid_create_task(client:TestClient, db:Session):
    image = create_test_image(db=db)
    user = image.uploaded_user

    response = client.post(
        "/task/",
        params={
            "created_user_id":user.id,
            "task_type": TaskType.bbox_annotation.value,
            "image_id": image.id,
        }
    )
    assert response.status_code == 200
    assert response.json()["task_type"] == TaskType.bbox_annotation.value
    assert response.json()["created_user_id"] == user.id
    assert response.json()["image_id"] == image.id
    assert response.json()["status"] == TaskStatus.pending.value

def test_invalid_image_create_task(client:TestClient, db:Session):
    user = create_test_user(db=db)

    response = client.post(
        "/task/",
        params={
            "created_user_id":user.id,
            "task_type":TaskType.bbox_annotation.value,
            "image_id": 0
        }
    )
    assert response.status_code == 404

def test_invalid_user_create_task(client:TestClient, db:Session):
    image = create_test_image(db=db)

    response = client.post(
        "/task/",
        params={
            "created_user_id":-1,
            "task_type":TaskType.bbox_annotation.value,
            "image_id": image.id
        }
    )
    assert response.status_code == 404

def test_invalid_task_type_create_task(client:TestClient, db:Session):
    image = create_test_image(db=db)
    user = image.uploaded_user

    response = client.post(
        "/task/",
        params={
            "created_user_id":user.id,
            "task_type":'123',
            "image_id": image.id
        }
    )
    assert response.status_code == 422

def test_valid_get_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    response = client.get(f"/task/{task.id}")
    assert response.status_code == 200
    assert response.json()["created_user_id"] == task.created_user_id
    assert response.json()["task_type"] == task.task_type.value
    assert response.json()["image_id"] == task.image_id

def test_invalid_id_get_task(client:TestClient, db:Session):
    response = client.get(f"/task/{1}")
    assert response.status_code == 404

def test_valid_accept_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    assert task.status.value == TaskStatus.pending.value
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":task.created_user_id,
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value
    assert response.json()["accepted_user_id"] == task.created_user_id

def test_invalid_already_accepted_accept_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user1 = task.created_user
    user2 = create_test_user(db=db)
    
    assert task.status.value == TaskStatus.pending.value
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 200

    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user2.id,
        }
    )
    assert response.status_code == 400

def test_invalid_already_accepted_same_user_accept_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user1 = task.created_user
    
    assert task.status.value == TaskStatus.pending.value
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 200

    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 400

def test_invalid_task_id_accept_task(client:TestClient, db:Session):
    user1 = create_test_user(db=db)
    response = client.put(
        f"/task/-1/accept",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 404

def test_invalid_user_id_accept_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":-1,
        }
    )
    assert response.status_code == 404

def test_invalid_accept_finished_accept_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user1 = task.created_user

    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 200
    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 200
    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 400


def test_valid_finish_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user1 = task.created_user
    assert task.status.value == TaskStatus.pending.value

    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id,
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value
    assert response.json()["accepted_user_id"] == user1.id

    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.finished.value
    assert response.json()["accepted_user_id"] == user1.id

def test_invalid_another_user_finish_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user1 = task.created_user
    user2 = create_test_user(db=db)

    assert task.status.value == TaskStatus.pending.value

    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id,
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value
    assert response.json()["accepted_user_id"] == user1.id

    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user2.id,
        }
    )
    assert response.status_code == 401

def test_invalid_task_id_finish_task(client:TestClient, db:Session):
    user1 = create_test_user(db=db)

    response = client.put(
        f"/task/-1/finish",
        params={
            "user_id":user1.id,
        }
    )

    assert response.status_code == 404

def test_invalid_user_id_finish_task(client:TestClient, db:Session):
    task = create_test_task(db=db)

    assert task.status.value == TaskStatus.pending.value

    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":-1,
        }
    )

    assert response.status_code == 404

def test_invalid_finish_not_accepted_task(client: TestClient, db:Session):
    task = create_test_task(db=db)
    user1 = task.created_user
    
    assert task.status.value == TaskStatus.pending.value

    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user1.id,
        }
    )

    assert response.status_code == 400

def test_invalid_finish_finished_task(client: TestClient, db:Session):
    task = create_test_task(db=db)
    user1 = task.created_user
    assert task.status.value == TaskStatus.pending.value

    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id,
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value
    assert response.json()["accepted_user_id"] == user1.id

    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.finished.value
    assert response.json()["accepted_user_id"] == user1.id
    
    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user1.id,
        }
    )
    assert response.status_code == 400
