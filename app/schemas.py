from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.database import TaskType, TaskStatus


class SpeciesCreate(BaseModel):
    name: str

class Species(SpeciesCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserID(BaseModel):
    id: int

class UserCreate(BaseModel):
    username: str
    email: str
    hashed_password: str

class UserBase(BaseModel):
    username: str
    email: str

class User(UserID, UserBase):
    model_config = ConfigDict(from_attributes=True)

class UserFull(User):
    uploaded_images: list[Image] = []
    created_tasks: list[Task] = []
    accepted_task: list[Task] = []


class ImageID(BaseModel):
    id: int

class ImageCreate(BaseModel):
    species_id: int
    uploaded_user_id:int
    model_config = ConfigDict(from_attributes=True)

class ImageBase(ImageCreate):
    path:str

class Image(ImageID, ImageBase):
    species: Species
    
    uploaded_user: User
    uploaded_at: datetime

    tasks: list[Task] = []


class TaskID(BaseModel):
    id: int

class TaskBase(BaseModel):
    created_user_id: int
    task_type: TaskType
    image_id: int
    model_config = ConfigDict(from_attributes=True)

class Task(TaskID,TaskBase):
    image:Image

    status: TaskStatus

    created_user: User
    created_at: datetime
    
    accepted_user_id:int|None = None
    accepted_user: User|None = None
    accepted_at: datetime|None = None

    finished_at: datetime|None = None

    bboxes: list[BboxAnnotation] = []
    polygons: list[PolyAnnotation] = []

    
class BboxAnnotationID(BaseModel):
    id:int

class BboxAnnotationBase(BaseModel):
    bbox:str
    task_id: int

class BboxAnnotation(BboxAnnotationID, BboxAnnotationBase):
    model_config = ConfigDict(from_attributes=True)

class PolyAnnotationID(BaseModel):
    id:int

class PolyAnnotationBase(BaseModel):
    polygon:str
    task_id: int

class PolyAnnotationUpdate(PolyAnnotationID):
    polygon:str

class PolyAnnotation(PolyAnnotationID, PolyAnnotationBase):
    task: Task
    model_config = ConfigDict(from_attributes=True)