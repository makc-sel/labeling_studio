from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy import ForeignKey, create_engine, func, select
import enum
from datetime import datetime, timezone


class Base(DeclarativeBase):
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {*[(i.name, self.__getattribute__(i.name)) for i in self.__table__.columns],}>"

class Species(Base):
    __tablename__ = "species"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    
    uploaded_images: Mapped[list["Image"]] = relationship(back_populates="uploaded_user", lazy="selectin")
    
    created_tasks: Mapped[list["Task"]] = relationship(back_populates="created_user", primaryjoin="user.c.id==task.c.created_user_id", lazy="selectin")
    
    accepted_tasks: Mapped[list["Task"]] = relationship(back_populates="accepted_user", primaryjoin="user.c.id==task.c.accepted_user_id", lazy="selectin")


class Image(Base):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(unique=True)

    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    species: Mapped["Species"] = relationship()
    
    uploaded_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    uploaded_user: Mapped["User"] = relationship(back_populates="uploaded_images")
    uploaded_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now(timezone.utc))
    

    tasks: Mapped[list["Task"]] = relationship(back_populates="image",lazy="selectin")

class TaskStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    finished = "finished"

class TaskType(enum.Enum):
    bbox_annotation = "bbox_annotation"
    poly_annotation = "poly_annotation"
    nn_bbox_annotation = "nn_bbox_annotation"
    nn_poly_annotation = "nn_poly_annotation"
    bbox_verification = "bbox_verification"
    poly_verification = "poly_verification"


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    task_type: Mapped[TaskType]
    image_id: Mapped[int] = mapped_column(ForeignKey("image.id"))
    image: Mapped["Image"] = relationship(back_populates="tasks", foreign_keys=[image_id])

    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.pending)

    created_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_user : Mapped["User"] = relationship(back_populates="created_tasks", foreign_keys=[created_user_id])
    created_at: Mapped[datetime] = mapped_column(nullable=False,default=datetime.now(timezone.utc)) # , server_default=func.CURRENT_TIMESTAMP()
    
    accepted_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    accepted_user: Mapped["User"] = relationship(back_populates="accepted_tasks", foreign_keys=[accepted_user_id])
    accepted_at: Mapped[None|datetime] = mapped_column(nullable=True)

    finished_at: Mapped[None|datetime] = mapped_column(nullable=True)
    
    bboxes: Mapped[list["BboxAnnotation"]] = relationship(back_populates="task", primaryjoin="task.c.id==bbox_annotation.c.task_id", lazy="selectin")
    polygons: Mapped[list["PolyAnnotation"]] = relationship(back_populates="task", primaryjoin="task.c.id==poly_annotation.c.task_id", lazy="selectin")


class BboxAnnotation(Base):
    __tablename__ = "bbox_annotation"
    id: Mapped[int]=mapped_column(primary_key=True)
    bbox:Mapped[str] = mapped_column(nullable=False)

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    task:Mapped[Task] = relationship(back_populates="bboxes")
    # image_id: Mapped[int]=mapped_column(ForeignKey("image.id"))
    # image: Mapped["Image"] = relationship(back_populates="bbox_annotations")

    # user_id: Mapped["User"] = mapped_column(ForeignKey("user.id"))
    # user: Mapped[list["User"]] = relationship(back_populates="bboxes")


class PolyAnnotation(Base):
    __tablename__ = "poly_annotation"
    id: Mapped[int]=mapped_column(primary_key=True)
    polygon:Mapped[str] = mapped_column(nullable=False)

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    task:Mapped[Task] = relationship(back_populates="polygons")
    # image_id:Mapped[int]=mapped_column(ForeignKey("image.id"))
    # image: Mapped["Image"] = relationship(back_populates="poly_annotations")

    
    # user_id: Mapped["User"] = mapped_column(ForeignKey("user.id"))
    # user: Mapped[list["User"]] = relationship(back_populates="polygons")


engine = create_engine("sqlite+pysqlite:///database.db", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    from sqlalchemy_schemadisplay import create_schema_graph
    from sqlalchemy import MetaData
    import os
    os.environ["PATH"] += os.pathsep + r"C:\Users\m.v.selickij\Downloads\windows_10_cmake_Release_Graphviz-10.0.1-win64\Graphviz-10.0.1-win64\bin"
    graph = create_schema_graph(metadata=Base.metadata, engine=engine)
    graph.write_png("entity_relationship_diagram.png")


    with Session(engine) as session:
        admin = User(username="admin",email="admin@gmail.com",hashed_password="admin")
        
        img1 = Image(path="/data/storage_1/images/cell1.jpg", species="gallus gallus", uploaded_user=admin)
        
        img2 = Image(path="/data/storage_1/images/cell2.jpg", species="gallus gallus", uploaded_user=admin)

        task1 = Task(task_type=TaskType.bbox_annotation, image=img1, created_user=admin)
        task2 = Task(task_type=TaskType.poly_annotation, image=img1, created_user=admin)
        task3 = Task(task_type=TaskType.bbox_verification, image=img1, created_user=admin)
        
        task4 = Task(task_type=TaskType.bbox_annotation, image=img2, created_user=admin)

        user1 = User(username="Max", email="makc.sel@gmail.com", hashed_password="1234")
        user2 = User(username="Anon", email="anon@gmail.com", hashed_password="1234")

        task1.accepted_user = user2
        task1.accepted_at = datetime.now(timezone.utc)
        session.add_all([admin,user1,user2])
        session.commit()

        print(admin)

        print(img1, img1.created_at)
        print(task1, task1.accepted_user, task1.created_at, task1.accepted_at, task1.finished_at)
        print(user1)
        print(user2, user2.accepted_tasks)

    # user2 accepted task insert result in db
    # we should ensure that user who insert annotations is the same user that accept task
    with Session(engine) as session:
        bbox1 = BboxAnnotation(bbox="(12.3, 34.3), (23,56.3)", task=task1)
        bbox2 = BboxAnnotation(bbox="(0.3, 0.3), (13,13)", task=task1)

        task1.finished_at = datetime.now(timezone.utc)
        img1.bbox_annotated = True

        session.add_all([bbox1,bbox2])
        session.commit()


        print(img1)
        print(bbox1)
        print(bbox2)
        print(task1)
        print(task1.bboxes)

    with Session(engine) as session:
        res = session.execute(select(Task).where(Task.finished_at != None)).scalars()
        for i in res:
            print(i)
            for bbox in i.bboxes:
                print("\t",bbox)