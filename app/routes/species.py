from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import app.crud as crud
from app.core.database import get_db
from app.schemas import SpeciesCreate, Species
from app.routes.exception import *


species_router = APIRouter(prefix="/species", tags=["species"])

@species_router.get("/")
async def get_species(skip:int=0, limit:int=100, db:Session=Depends(get_db)) -> list[Species]:
    return crud.get_species(db=db,skip=skip,limit=limit)


@species_router.get("/{id:int}")
async def get_species_by_id(id:int, db:Session=Depends(get_db)) -> Species:
    species = crud.get_species_by_id(db=db,id=id)
    if not species:
        raise SpeciesNotFoundException
    return species

@species_router.post("/")
async def create_species(new_species: SpeciesCreate, db:Session=Depends(get_db)) -> Species:
    species = crud.get_species_by_name(db=db, name=new_species.name)
    if species:
        raise SpeciesNameExistedException
    species = crud.create_species(db=db, new_species=new_species)
    return species
    

@species_router.delete("/{id:int}")
async def delete_species(id:int, db:Session=Depends(get_db)) -> Species:
    pass
