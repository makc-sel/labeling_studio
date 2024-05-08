from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.tests.utils.image import create_test_image
from app.tests.utils.species import create_test_species
from app.tests.utils.user import create_test_user
from app.tests.utils.task import create_test_task
from app.core.database import TaskType, TaskStatus
from app.settings import image_domain
from app.routes.exception import *

def test_valid_create_bbox(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value

    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )
    assert response.status_code == 200
    assert response.json()["task_id"] == task.id
    assert response.json()["bbox"] == bbox["bbox"]
    resp_bbox = response.json()

    response = client.get(f"/task/{task.id}")
    assert response.json()["bboxes"] == [resp_bbox]

def test_invalid_create_bbox_bad_user(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value

    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":-1,
        },
        json = bbox
    )
    assert response.status_code == 404
    assert response.json()["detail"] == UserNotFoundException.detail

def test_invalid_create_bbox_not_same_user(client:TestClient, db:Session):
    task = create_test_task(db=db)
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

    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user2.id,
        },
        json = bbox
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddAnnotationFromNotAcceptedUser.detail

def test_invalid_create_bbox_bad_task(client:TestClient, db:Session):
    user = create_test_user(db=db)
    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": -1
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )
    assert response.status_code == 404
    assert response.json()["detail"] == TaskNotFoundException.detail

def test_invalid_create_bbox_pending_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user = task.created_user
    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddAnnotationToPendingTaskException.detail

def test_invalid_create_bbox_finished_task(client:TestClient, db:Session):
    task = create_test_task(db=db)
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

    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddAnnotationToFinishedTaskException.detail

def test_invalid_create_bbox_bad_bbox(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    bbox = {
        "poly":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )
    assert response.status_code == 422

def test_invalid_create_bbox_bad_task_type(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.poly_annotation.value)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )
    assert response.status_code == 400
    assert response.json()["detail"] == AddBboxToPolygonTaskTypeException.detail

def test_valid_update_bbox(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.bbox_annotation.value)
    user = task.created_user
    # accept task
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }
    # add bbox to task
    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )

    assert response.status_code == 200
    bbox = response.json()

    # update bbox
    response = client.put(
        f"/bbox/update/{bbox["id"]}",
        params={
            "user_id":user.id,
            "new_bbox":"(3,3),(10,10)"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"id":bbox["id"],"bbox":"(3,3),(10,10)","task_id":bbox["task_id"]}

def test_valid_create_many_bboxes(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.bbox_annotation.value)
    user = task.created_user
    # accept task
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    bbox1 = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }
    bbox2 = {
        "bbox":"(3,3),(4,4)",
        "task_id": task.id
    }
    # add bbox to task
    response = client.post(
        "/bbox/createmany",
        params={
            "user_id":user.id,
        },
        json = [
                bbox1,
                bbox2
            ]
    )
    assert response.status_code == 200
    assert response.json()[0]['bbox'] == bbox1['bbox']
    assert response.json()[0]['task_id'] == bbox1['task_id']
    assert response.json()[0]['id'] == 1
    
    assert response.json()[1]['bbox'] == bbox2['bbox']
    assert response.json()[1]['task_id'] == bbox2['task_id']
    assert response.json()[1]['id'] == 2

    bbox1["id"]=response.json()[0]['id']
    bbox2["id"]=response.json()[1]['id']

    # check task
    response = client.get(f"/task/{task.id}")
    assert response.status_code == 200
    assert response.json()['bboxes'] == [bbox1,bbox2]

def test_invalid_create_many_bboxes_bad_task_id(client:TestClient, db:Session):
    task = create_test_task(db=db, task_type=TaskType.bbox_annotation.value)
    user = task.created_user
    # accept task
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    bbox1 = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }
    bbox2 = {
        "bbox":"(3,3),(4,4)",
        "task_id": -1
    }
    # add bbox to task
    response = client.post(
        "/bbox/createmany",
        params={
            "user_id":user.id,
        },
        json = [
                bbox1,
                bbox2
            ]
    )
    assert response.status_code == 404
    assert response.json()["detail"] == TaskNotFoundException.detail

def test_valid_delete_bbox(client:TestClient, db:Session):
    task = create_test_task(db=db)
    user = task.created_user
    
    response = client.put(
        f"/task/{task.id}/accept",
        params={
            "user_id":user.id
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.accepted.value

    bbox = {
        "bbox":"(1,1),(2,2)",
        "task_id": task.id
    }

    response = client.post(
        "/bbox/create",
        params={
            "user_id":user.id,
        },
        json = bbox
    )
    assert response.status_code == 200
    assert response.json()["task_id"] == task.id
    assert response.json()["bbox"] == bbox["bbox"]
    resp_bbox = response.json()

    response = client.get(f"/task/{task.id}")
    assert response.json()["bboxes"] == [resp_bbox]

    response = client.delete(
        f"/bbox/delete/{resp_bbox["id"]}",
        params={
            "user_id": user.id
        }
    )
    assert response.status_code == 200
    assert response.json() == resp_bbox["id"]

    response = client.get(f"/task/{task.id}")
    assert response.json()["bboxes"] == []


# createmany pending taskstatus
# createmany finished taskstatus
# createmany wrong tasktype
# createmany bad user
# createmany not accepted user
# delete bad bbox_id