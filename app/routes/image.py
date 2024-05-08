import os
import uuid
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import aiofiles
import app.crud as crud
from app.core.database import get_db
from app.schemas import Image, ImageBase, ImageCreate
from app.routes.exception import *
from app.settings import image_domain

image_router = APIRouter(prefix="/image", tags=["image"])

@image_router.get("/")
async def get_images(skip:int=0, limit:int=100, species_id:int|None=None, db:Session=Depends(get_db)) -> list[Image]:
    return crud.get_images(db=db, skip=skip,limit=limit,species_id=species_id)

@image_router.get("/{id:int}")
async def get_image(id:int, db:Session=Depends(get_db)) -> Image:
    image = crud.get_image_by_id(db=db,id=id)
    if not image:
        raise ImageNotFoundException
    return image

@image_router.get("/{id:int}/download")
async def download_image(id:int, db:Session=Depends(get_db)) -> FileResponse:
    image = crud.get_image_by_id(db=db,id=id)
    if not image:
        raise ImageNotFoundException
    return FileResponse(path=image_domain + image.path, headers={"filename": image.path.split('/')[-1]})

@image_router.post("/")
async def upload_image(
    image_file: UploadFile = File(...),
    image_data: ImageCreate = Depends(),
    db:Session=Depends(get_db)
) -> Image:
    # first of all we need to take an image and place it somewhere 
    # (in our domain, like c:/data/images/ - it's our constant path (domain)
    # in db we need to store image path without domain like 1.jpg, or /gallus/1.jpg)
    # then we need to get relative path and add it to an image entity
    # and create entity like below
    # id = 1, path = "/gallus/u1opsad.jpg", species_id = 1, uploaded_user_id = 1, uploaded_at="sometime"
    
    species = crud.get_species_by_id(db=db,id=image_data.species_id)
    if not species:
        raise SpeciesNotFoundException
    
    user = crud.get_user_by_id(db=db,user_id=image_data.uploaded_user_id)
    if not user:
        raise UserNotFoundException

    # store images like /species/image_uuid.jpg
    image_path_without_domain = '/' + species.name + '/'
    image_path_with_domain = image_domain + image_path_without_domain

    # check species folder exist
    if not os.path.exists(image_path_with_domain):
        os.mkdir(image_path_with_domain)
    
    # generate out_file_path
    out_file_path = str(uuid.uuid4())+'.'+image_file.filename.split('.')[-1]
    while os.path.exists(image_path_with_domain+'/'+out_file_path):
        out_file_path = str(uuid.uuid4())+'.'+image_file.filename.split('.')[-1]

    # check that file is image
    async with aiofiles.open(image_path_with_domain+'/'+out_file_path, 'wb') as fout:
        while content := await image_file.read(1024): # async read chunk
            await fout.write(content) # async write chunk
    
    image = crud.create_image(db=db,image=ImageBase(**image_data.model_dump(), path=image_path_without_domain+'/'+out_file_path))
    return image

@image_router.put("/{id:int}")
async def change_image_species(id: int, new_species:str, db:Session=Depends(get_db)) -> Image:
    #TODO
    pass
