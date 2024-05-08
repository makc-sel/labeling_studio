import os
import uuid
from sqlalchemy.orm import Session
from app import crud
from app.schemas import Task, TaskBase
from app.core.database import TaskType

from app.settings import image_domain
from .image import create_test_image

def create_test_task(db:Session, task_type=TaskType.bbox_annotation.value)->Task:
    image = create_test_image(db=db)
    user = image.uploaded_user
    task = crud.create_task(
        db=db,
        new_task=TaskBase(
            created_user_id=user.id,
            task_type=task_type,
            image_id=image.id
        )
    )
    return task