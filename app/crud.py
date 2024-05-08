from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update
from app.core import database
from app import schemas


# Users
def get_users(db:Session,skip=0, limit=100) -> list[database.User]:
    return db.execute(select(database.User).offset(skip).limit(limit)).scalars()

def get_user_by_id(db:Session, user_id:int) -> database.User:
    return db.get(database.User, user_id)
    
def get_user_by_email(db:Session, email:str) -> database.User:
    return db.execute(select(database.User).filter(database.User.email==email)).scalar()

def get_user_by_username(db:Session, username:str) -> database.User:
    return db.execute(select(database.User).filter(database.User.username==username)).scalar()

def create_user(db:Session, new_user:schemas.UserCreate) -> database.User:
    db_user = database.User(username=new_user.username, email=new_user.email, hashed_password=new_user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Task
def get_tasks(db:Session, skip=0, limit=100, task_type:schemas.TaskType=None, task_status: database.TaskStatus=None) -> list[database.Task]:
    conditions = []
    if task_type is not None:
        conditions.append(database.Task.task_type == task_type)
    if task_status is not None:
        conditions.append(database.Task.status == task_status)

    return db.execute(select(database.Task).filter(*conditions).offset(skip).limit(limit)).scalars()
   
def get_task_by_id(db:Session, id:int) -> database.Task:
    return db.get(database.Task, id)

def get_tasks_by_image(db:Session, image_id:int) -> database.Task:
    return db.execute(select(database.Task).filter_by(image_id=image_id)).scalars()

def create_task(db:Session, new_task:schemas.TaskBase) -> database.Task:
    db_task = database.Task(
        **new_task.model_dump(),
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def accept_task(db:Session, id:int, user_id:int) -> database.Task:
    task = get_task_by_id(db=db, id=id)
    task.accepted_user_id = user_id
    task.accepted_at = datetime.now(timezone.utc)
    task.status = database.TaskStatus.accepted
    db.commit()
    db.refresh(task)
    return task

def finish_task(db:Session, id:int) -> database.Task:
    task = get_task_by_id(db=db, id=id)
    task.finished_at = datetime.now(timezone.utc)
    task.status = database.TaskStatus.finished
    db.commit()
    db.refresh(task)
    return task


# Images
def get_image_by_id(db:Session, id:int) -> database.Image:
    image = db.get(database.Image, id)
    return image

def get_images(db:Session, skip=0, limit=100, species_id:int|None=None) -> list[database.Image]:
    if species_id:
        return db.execute(select(database.Image).filter(database.Image.species_id == species_id).offset(skip).limit(limit))
    return db.execute(select(database.Image).offset(skip).limit(limit)).scalars()

def create_image(db:Session, image:schemas.ImageBase) -> database.Image:
    db_image = database.Image(
        **image.model_dump(),
        uploaded_at = datetime.now(timezone.utc)
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def update_image_species():
    pass


# Species
def get_species(db:Session, skip:int=0, limit:int=100) -> list[database.Species]:
    species = db.execute(select(database.Species).offset(skip).limit(limit)).scalars()
    return species

def get_species_by_id(db:Session, id:int) -> database.Species:
    species = db.get(database.Species, id)
    return species

def get_species_by_name(db:Session, name:str) -> database.Species:
    species = db.execute(select(database.Species).filter(database.Species.name == name)).scalar()
    return species

def create_species(db:Session, new_species: schemas.SpeciesCreate) -> database.Species:
    db_species = database.Species(**new_species.model_dump())
    db.add(db_species)
    db.commit()
    db.refresh(db_species)
    return db_species
    
def delete_species(db:Session):
    # check image with given species existed
    # check any other relationship with given species
    pass

# BBOXES
def get_bboxes(db:Session, skip=0, limit=100, task_id:int|None=None) -> list[database.BboxAnnotation]:
    if task_id:
        return db.execute(select(database.BboxAnnotation).filter(database.BboxAnnotation.task_id == task_id).offset(skip).limit(limit))
    return db.execute(select(database.BboxAnnotation).offset(skip).limit(limit)).scalars()


def get_bbox_by_id(db:Session, bbox_id:int) -> database.BboxAnnotation:
    bbox = db.get(database.BboxAnnotation, bbox_id)
    return bbox

def create_bboxes(db:Session, new_bboxes: list[schemas.BboxAnnotationBase]) -> list[database.BboxAnnotation]:
    # # not add relationship
    # return db.scalars(
    #     insert(database.BboxAnnotation).returning(database.BboxAnnotation),
    #     new_bboxes
    # ).all()

    db_bboxes = [database.BboxAnnotation(**new_bbox.model_dump()) for new_bbox in new_bboxes]
    db.add_all(db_bboxes)
    db.commit()
    for db_bbox in db_bboxes:
        db.refresh(db_bbox)
    return db_bboxes


def create_bbox(db:Session, new_bbox: schemas.BboxAnnotationBase) -> database.BboxAnnotation:
    db_bbox = database.BboxAnnotation(**new_bbox.model_dump())
    db.add(db_bbox)
    db.commit()
    db.refresh(db_bbox)
    return db_bbox

def update_bbox_by_id(db:Session, bbox_id:int, new_bbox:str) -> database.BboxAnnotation:
    # 2 queries to db
    db_bbox = get_bbox_by_id(db=db, bbox_id=bbox_id)
    db_bbox.bbox = new_bbox
    db.commit()
    db.refresh(db_bbox)

    # # 1 query to db
    # stmt = (
    #     update(database.BboxAnnotation.__table__)
    #     .values(bbox=new_bbox)
    #     .filter_by(id=bbox_id)
    #     .returning(database.BboxAnnotation)
    # )
    # db_bbox = db.execute(stmt).scalar()
    
    return db_bbox

def delete_bbox_by_id(db:Session, bbox_id:int):
    db_bbox = get_bbox_by_id(db=db, bbox_id=bbox_id)
    db.delete(db_bbox)
    db.commit()
    return bbox_id

# POLYGONS
def get_polygons(db:Session, skip=0, limit=100, task_id:int|None=None) -> list[database.PolyAnnotation]:
    if task_id:
        return db.execute(select(database.PolyAnnotation).filter(database.PolyAnnotation.task_id == task_id).offset(skip).limit(limit))
    return db.execute(select(database.PolyAnnotation).offset(skip).limit(limit)).scalars()

def get_polygon_by_id(db:Session, polygon_id:int) -> database.PolyAnnotation:
    polygon = db.get(database.PolyAnnotation, polygon_id)
    return polygon

def create_polygon(db:Session, new_polygon: schemas.PolyAnnotationBase) -> database.PolyAnnotation:
    db_polygon = database.PolyAnnotation(**new_polygon.model_dump())
    db.add(db_polygon)
    db.commit()
    db.refresh(db_polygon)
    return db_polygon

def create_polygons(db:Session, new_polygons: list[schemas.PolyAnnotationBase]) -> list[database.PolyAnnotation]:
    db_polygons = [database.PolyAnnotation(**new_polygon.model_dump()) for new_polygon in new_polygons]
    db.add_all(db_polygons)
    db.commit()
    for db_polygon in db_polygons:
        db.refresh(db_polygon)
    return db_polygons

def update_polygon_by_id(db:Session, polygon_id:int, new_polygon:str) -> database.PolyAnnotation:
    db_polygon = get_polygon_by_id(db=db, polygon_id=polygon_id)
    db_polygon.polygon = new_polygon
    db.commit()
    db.refresh(db_polygon)
    return db_polygon

def delete_polygon_by_id(db:Session, polygon_id:int):
    db_polygon = get_polygon_by_id(db=db, polygon_id=polygon_id)
    db.delete(db_polygon)
    db.commit()
    return polygon_id
