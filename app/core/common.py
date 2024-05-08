from sqlalchemy.orm import Session

from app import crud
from app.core.database import TaskStatus, TaskType
from app.routes.exception import *
from typing import Literal

_TYPES = Literal["bbox", "poly"]
def check_task(db:Session, user_id:int,task_id:int,type:_TYPES="bbox"):
    task = crud.get_task_by_id(db=db, id=task_id)
    if not task:
        raise TaskNotFoundException

    if task.status.value == TaskStatus.pending.value:
        raise AddAnnotationToPendingTaskException

    if task.status.value == TaskStatus.finished.value:
        raise AddAnnotationToFinishedTaskException
    
    if type == "poly":
        if task.task_type.value in [TaskType.bbox_annotation.value,TaskType.bbox_verification.value, TaskType.nn_bbox_annotation.value]:
            raise AddPolygonToBboxTaskTypeException
    elif type == "bbox":
        if task.task_type.value in [TaskType.poly_annotation.value,TaskType.poly_verification.value, TaskType.nn_poly_annotation.value]:
            raise AddBboxToPolygonTaskTypeException
        
    if task.accepted_user_id != user_id:
        raise AddAnnotationFromNotAcceptedUser
    return task

def check_user(db:Session, user_id:int):
    user = crud.get_user_by_id(db=db,user_id=user_id)
    if not user:
        raise UserNotFoundException
    return user