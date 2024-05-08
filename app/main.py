from fastapi import FastAPI
from app.routes.image import image_router
from app.routes.task import task_router
from app.routes.user import user_router
from app.routes.species import species_router
from app.routes.bbox import bbox_router
from app.routes.polygon import poly_router
from app.core.database import Base, engine

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(image_router)
app.include_router(task_router)
app.include_router(user_router)
app.include_router(species_router)
app.include_router(bbox_router)
app.include_router(poly_router)
