from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.common import check_task, check_user
from app.schemas import BboxAnnotationBase
from app.routes.exception import *

# TODO update many, Delete many
 
bbox_router = APIRouter(prefix="/bbox", tags=["bbox"])

@bbox_router.get("/")
async def get_bboxes(
    skip=0,
    limit=100,
    task_id:int|None=None,
    db:Session=Depends(get_db)
):
    bboxes = crud.get_bboxes(db=db, skip=skip,limit=limit, task_id=task_id)
    return bboxes

@bbox_router.get("/{bbox_id:int}")
async def get_bbox(bbox_id:int, db:Session=Depends(get_db)):
    bbox = crud.get_bbox_by_id(db=db,bbox_id=bbox_id)
    if not bbox:
        raise BboxNotFoundException
    return bbox

@bbox_router.post("/create")
async def create_bbox(user_id:int, new_bbox:BboxAnnotationBase, db:Session=Depends(get_db)):
    user = check_user(db=db, user_id=user_id)
    task = check_task(db=db,user_id=user.id, task_id=new_bbox.task_id, type="bbox")

    bbox = crud.create_bbox(db=db, new_bbox=new_bbox)
    return bbox

@bbox_router.post("/createmany")
async def create_bboxes(user_id:int, new_bboxes:list[BboxAnnotationBase], db:Session=Depends(get_db)):
    # add all or nothing
    user = check_user(db=db, user_id=user_id)
    tasks_id = set([i.task_id for i in new_bboxes])
    for task_id in tasks_id:
        task = check_task(db=db,user_id=user.id, task_id=task_id, type="bbox")
    bboxes = crud.create_bboxes(db=db, new_bboxes=new_bboxes)
    return bboxes

@bbox_router.put("/update/{bbox_id:int}")
async def update_bbox(bbox_id:int, user_id:int, new_bbox:str, db:Session=Depends(get_db)):
    user = check_user(db=db, user_id=user_id)
    # TODO check task is opened
    bbox = crud.get_bbox_by_id(db=db, bbox_id=bbox_id)
    if not bbox:
        raise BboxNotFoundException

    bbox = crud.update_bbox_by_id(db=db,bbox_id=bbox_id,new_bbox=new_bbox)
    return bbox

# @bbox_router.put("/updatemany/")
# async def update_bboxes(bboxes_id:list[int], user_id:int, new_bboxes:list[int], db:Session=Depends(get_db)):
#     pass

@bbox_router.delete("/delete/{bbox_id:int}")
async def delete_bbox(bbox_id:int, user_id:int, db:Session=Depends(get_db)):
    # TODO check task is opened
    bbox = crud.get_bbox_by_id(db=db, bbox_id=bbox_id)
    if not bbox:
        raise BboxNotFoundException
    user = check_user(db=db,user_id=user_id)

    bbox = crud.delete_bbox_by_id(db=db,bbox_id=bbox_id)
    return bbox