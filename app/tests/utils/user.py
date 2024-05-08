from sqlalchemy.orm import Session
from app import crud
from app.schemas import UserCreate, User
import random
import string


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email():
    return f"{random_lower_string()}@{random_lower_string()}.com"


def create_test_user(db:Session) -> User:
    user = crud.create_user(
        db=db,
        new_user=UserCreate(
            username=random_lower_string(),
            email=random_email(),
            hashed_password="test"
        )
    )

    return User.model_validate(user)