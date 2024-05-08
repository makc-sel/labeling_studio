from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import app.crud as crud
from app.core.database import get_db, TaskType, TaskStatus
from app.schemas import Task,TaskBase
from app.routes.exception import *

task_router = APIRouter(prefix="/task", tags=["task"])
# TODO replace logic into new place, maybe class

@task_router.get("/")
async def get_tasks(
    task_status:TaskStatus=None,
    task_type:TaskType=None,
    skip=0,
    limit=100,
    db:Session=Depends(get_db)
) -> list[Task]:
    tasks = crud.get_tasks(task_status=task_status,task_type=task_type,skip=skip,limit=limit,db=db)
    return tasks


@task_router.get("/{id:int}")
async def get_task_by_id(
    id:int,
    db:Session=Depends(get_db)
):
    task = crud.get_task_by_id(db=db, id=id)
    if not task:
        raise TaskNotFoundException
    return task


@task_router.post("/")
async def create_task(
    new_task:TaskBase=Depends(),
    db:Session=Depends(get_db)
):
    user = crud.get_user_by_id(user_id=new_task.created_user_id, db=db)
    if not user:
        raise UserNotFoundException
    
    image = crud.get_image_by_id(id=new_task.image_id,db=db)
    if not image:
        raise ImageNotFoundException
    
    task = crud.create_task(db=db, new_task=new_task)
    return task


@task_router.put("/{id:int}/accept")
async def accept_task(
    id:int,
    user_id:int,
    db:Session=Depends(get_db)
):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise UserNotFoundException
    
    task = crud.get_task_by_id(db=db,id=id)
    if not task:
        raise TaskNotFoundException
    
    if task.status.value == TaskStatus.accepted.value:
        raise TaskAcceptAcceptedException

    if task.status.value == TaskStatus.finished.value:
        raise TaskAcceptFinishedException

    task = crud.accept_task(db=db,id=id,user_id=user_id)
    return task


@task_router.put("/{id:int}/finish")
async def finish_task(
    id:int,
    user_id:int,
    db:Session=Depends(get_db)
):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise UserNotFoundException
    
    task = crud.get_task_by_id(db=db,id=id)
    if not task:
        raise TaskNotFoundException
    
    if task.status.value == TaskStatus.pending.value:
        raise TaskFinishNotAcceptedTaskError
    
    if task.status.value == TaskStatus.finished.value:
        raise TaskFinishFinishedTaskError
    
    if user.id != task.accepted_user_id:
        raise TaskFinishUserNotSame

    task = crud.finish_task(db=db,id=id)
    return task
