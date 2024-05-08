import os
import uuid
from sqlalchemy.orm import Session
from app import crud
from app.schemas import UserCreate, SpeciesCreate, ImageBase, Image

from app.settings import image_domain


def create_test_image(db:Session) -> Image:
    user = crud.create_user(
        db=db,
        new_user=UserCreate(
            username="test",
            email="test@gmail.com",
            hashed_password="test"
        )
    )
    species = crud.create_species(
        new_species=SpeciesCreate(name="test_species"),
        db=db
    )

    image_path_without_domain = '/'+species.name+'/'
    image_path_with_domain = image_domain + image_path_without_domain

    if not os.path.exists(image_path_with_domain):
        os.mkdir(image_path_with_domain)
    
    out_file_path = str(uuid.uuid4())+'.jpg'
    while os.path.exists(image_path_with_domain+'/'+out_file_path):
        out_file_path = str(uuid.uuid4())+'.jpg'

    import shutil
    shutil.copy(
        "app/tests/data/test_image.jpg",
        image_path_with_domain+'/'+out_file_path
    )

    image = crud.create_image(db=db,image=ImageBase(species_id=species.id, uploaded_user_id=user.id, path=image_path_without_domain+'/'+out_file_path))
    return Image.model_validate(image)