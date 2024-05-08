from sqlalchemy.orm import Session
from app import crud
from app.schemas import Species, SpeciesCreate

def create_test_species(db:Session) -> Species:
    species = crud.create_species(
        new_species=SpeciesCreate(name="test_species"),
        db=db
    )
    return Species.model_validate(species)