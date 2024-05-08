import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.tests.utils.image import create_test_image
from app.tests.utils.species import create_test_species
from app.tests.utils.user import create_test_user
from app.settings import image_domain

#TODO test get many images

def test_valid_create_image(
        client: TestClient,
        db:Session
):
    species = create_test_species(db=db)
    user = create_test_user(db=db)

    with open(rf"app\tests\data\test_upload.png",'rb') as fout:
        response = client.post(
                "/image/",
                params={
                    "species_id":species.id,
                    "uploaded_user_id":user.id
                },
                files={
                      "image_file":
                      fout
                }
        )
    assert response.status_code==200
    assert response.json()["id"] == 1
    assert response.json()["uploaded_user_id"] == user.id
    assert response.json()["species_id"] == species.id

    assert os.path.exists(image_domain+response.json()["path"])

def test_invalid_species_create_image(client:TestClient, db:Session):
    user = create_test_user(db=db)

    with open(rf"app\tests\data\test_upload.png",'rb') as fout:
            response = client.post(
                    "/image/",
                    params={
                        "species_id":"1",
                        "uploaded_user_id":user.id
                    },
                    files={
                          "image_file":
                          fout
                }
            )
    assert response.status_code==404

def test_invalid_user_create_image(client:TestClient, db:Session):
    species = create_test_species(db=db)

    with open(rf"app\tests\data\test_upload.png",'rb') as fout:
            response = client.post(
                    "/image/",
                    params={
                        "species_id":species.id,
                        "uploaded_user_id":"123"
                    },
                    files={
                          "image_file":
                          fout
                }
            )
    assert response.status_code==404

def test_valid_download_image(client:TestClient, db:Session):
    import filecmp
    image = create_test_image(db=db)
    response = client.get(f"/image/{image.id}/download")
    assert response.status_code == 200
    assert response.headers["filename"] == image.path.split("/")[-1]
    # save file
    with open(response.headers["filename"], 'wb') as fin:
        fin.write(response.content)
    # uploaded and downloaded images the same
    assert filecmp.cmp(response.headers["filename"], image_domain+image.path)
    # remove downloaded image
    os.remove(response.headers["filename"])

def test_invalid_image_id_download_image(client:TestClient, db:Session):
    response = client.get(f"/image/{1}/download")
    assert response.status_code == 404

def test_valid_get_image(client:TestClient, db:Session):
    image = create_test_image(db=db)

    resp = client.get(f"/image/{image.id}")
    assert resp.status_code == 200
    assert resp.json()["species_id"] == image.species_id
    assert resp.json()["uploaded_user_id"] == image.uploaded_user_id
    assert resp.json()["tasks"] == image.tasks
    assert resp.json()["path"] == image.path

def test_invalid_image_id_get_image(client:TestClient, db:Session):
    resp = client.get(f"/image/{1}")
    assert resp.status_code == 404