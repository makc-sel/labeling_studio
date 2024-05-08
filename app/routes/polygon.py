from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.common import check_task, check_user
from app.schemas import PolyAnnotationBase
from app.routes.exception import *

# TODO update many, Delete many

poly_router = APIRouter(prefix="/polygon", tags=["polygon"])

@poly_router.get("/")
async def get_polygons(
    skip=0,
    limit=100,
    task_id:int|None=None,
    db:Session=Depends(get_db)
):
    polygons = crud.get_polygons(db=db, skip=skip,limit=limit, task_id=task_id)
    return polygons

@poly_router.get("/{polygon_id:int}")
async def get_polygon(polygon_id:int, db:Session=Depends(get_db)):
    polygon = crud.get_polygon_by_id(db=db, polygon_id=polygon_id)
    if not polygon:
        raise PolygonNotFoundException
    return polygon

@poly_router.post("/create")
async def create_polygon(user_id:int, new_polygon:PolyAnnotationBase, db:Session=Depends(get_db)):
    user = check_user(db=db, user_id=user_id)
    task = check_task(db=db,user_id=user.id, task_id=new_polygon.task_id, type="poly")

    polygon = crud.create_polygon(db=db, new_polygon=new_polygon)
    return polygon

@poly_router.post("/createmany")
async def create_polygons(user_id:int, new_polygons:list[PolyAnnotationBase], db:Session=Depends(get_db)):
    # add all or nothing
    user = check_user(db=db,user_id=user_id)
    tasks_id = set([i.task_id for i in new_polygons])
    for task_id in tasks_id:
        task = check_task(db=db,user_id=user.id, task_id=task_id, type="poly")
    poygons = crud.create_polygons(db=db, new_polygons=new_polygons)
    return poygons

@poly_router.put("/update/{polygon_id:int}")
async def update_polygon(polygon_id:int, user_id:int, new_polygon:str, db:Session=Depends(get_db)):
    user = check_user(db=db, user_id=user_id)
    # TODO check task is opened
    polygon = crud.get_polygon_by_id(db=db, polygon_id=polygon_id)
    if not polygon:
        raise PolygonNotFoundException

    polygon = crud.update_polygon_by_id(db=db, polygon_id=polygon_id, new_polygon=new_polygon)
    return polygon

# @poly_router.put("/updatemany/")
# async def update_polygons(polygons_id:list[int], user_id:int, new_polygons:list[str], db:Session=Depends(get_db)):
#     pass

@poly_router.delete("/delete/{polygon_id:int}")
async def delete_bbox(polygon_id:int, user_id:int, db:Session=Depends(get_db)):
    # TODO check task is opened
    polygon = crud.get_polygon_by_id(db=db, polygon_id=polygon_id)
    if not polygon:
        raise PolygonNotFoundException
    user = check_user(db=db,user_id=user_id)

    polygon = crud.delete_polygon_by_id(db=db,polygon_id=polygon_id)
    return polygon