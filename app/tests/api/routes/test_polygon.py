from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.tests.utils.image import create_test_image
from app.tests.utils.species import create_test_species
from app.tests.utils.user import create_test_user
from app.tests.utils.task import create_test_task
from app.core.database import TaskType, TaskStatus
from app.settings import image_domain
from app.routes.exception import *

def test_valid_create_polygon(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value

    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )
    assert response.status_code == 200
    assert response.json()["task_id"] == task.id
    assert response.json()["polygon"] == polygon["polygon"]
    resp_polygon = response.json()

    response = client.get(f"/task/{task.id}")
    assert response.json()["polygons"] == [resp_polygon]

def test_invalid_create_polygon_bad_user(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value

    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":-1,
        },
        json = polygon
    )
    assert response.status_code == 404
    assert response.json()["detail"] == UserNotFoundException.detail

def test_invalid_create_polygon_not_same_user(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user1 = task.created_user
    user2 = create_test_user(db=db)
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user1.id
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value

    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user2.id,
        },
        json = polygon
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddAnnotationFromNotAcceptedUser.detail

def test_invalid_create_polygon_bad_task(client:TestClient, db:Session):
    user = create_test_user(db=db)
    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": -1
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )
    assert response.status_code == 404
    assert response.json()["detail"] == TaskNotFoundException.detail

def test_invalid_create_polygon_pending_task(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddAnnotationToPendingTaskException.detail

def test_invalid_create_polygon_finished_task(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    response = client.put(
        f"/task/{task.id}/finish",
        params={
            "user_id":user.id
        }
    )

    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddAnnotationToFinishedTaskException.detail

def test_invalid_create_polygon_bad_polygon(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    polygon = {
        "bbox":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )
    assert response.status_code == 422

def test_invalid_create_polygon_bad_task_type(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.bbox_annotation.value)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddPolygonToBboxTaskTypeException.detail

def test_valid_update_polygon(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    # accept task
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }
    # add polygon to task
    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )

    assert response.status_code == 200
    polygon = response.json()

    # update polygon
    response = client.put(
        f"/polygon/update/{polygon["id"]}",
        params={
            "user_id":user.id,
            "new_polygon":"(1,1),(2,2),(3,3),(4,4),(5,5),(3,3),(10,10)"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"id":polygon["id"],"polygon":"(1,1),(2,2),(3,3),(4,4),(5,5),(3,3),(10,10)","task_id":polygon["task_id"]}

def test_valid_create_many_polygons(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    # accept task
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    polygon1 = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }
    polygon2 = {
        "polygon":"(6,1),(7,2),(8,3),(9,4),(10,5)",
        "task_id": task.id
    }
    # add polygons to task
    response = client.post(
        "/polygon/createmany",
        params={
            "user_id":user.id,
        },
        json = [
                polygon1,
                polygon2
            ]
    )
    assert response.status_code == 200
    assert response.json()[0]['polygon'] == polygon1['polygon']
    assert response.json()[0]['task_id'] == polygon1['task_id']
    assert response.json()[0]['id'] == 1
    
    assert response.json()[1]['polygon'] == polygon2['polygon']
    assert response.json()[1]['task_id'] == polygon2['task_id']
    assert response.json()[1]['id'] == 2

    polygon1["id"]=response.json()[0]['id']
    polygon2["id"]=response.json()[1]['id']

    # check task
    response = client.get(f"/task/{task.id}")
    assert response.status_code == 200
    assert response.json()['polygons'] == [polygon1,polygon2]

def test_invalid_create_many_polygons_bad_task_id(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    # accept task
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    polygon1 = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }
    polygon2 = {
        "polygon":"(6,1),(7,2),(8,3),(9,4),(10,5)",
        "task_id": -1
    }
    # add polygon to task
    response = client.post(
        "/polygon/createmany",
        params={
            "user_id":user.id,
        },
        json = [
                polygon1,
                polygon2
            ]
    )
    assert response.status_code == 404
    assert response.json()["detail"] == TaskNotFoundException.detail

def test_valid_create_polygon(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value

    polygon = {
        "polygon":"(1,1),(2,2),(3,3),(4,4),(5,5)",
        "task_id": task.id
    }

    response = client.post(
        "/polygon/create",
        params={
            "user_id":user.id,
        },
        json = polygon
    )
    assert response.status_code == 200
    assert response.json()["task_id"] == task.id
    assert response.json()["polygon"] == polygon["polygon"]
    resp_polygon = response.json()

    response = client.get(f"/task/{task.id}")
    assert response.json()["polygons"] == [resp_polygon]

    response = client.delete(
        f"/polygon/delete/{resp_polygon["id"]}",
        params={
            "user_id": user.id
        }
    )
    assert response.status_code == 200
    assert response.json() == resp_polygon["id"]

    response = client.get(f"/task/{task.id}")
    assert response.json()["polygons"] == []

# createmany pending taskstatus
# createmany finished taskstatus
# createmany wrong tasktype
# createmany bad user
# createmany not accepted user
# delete bad polygon_id