import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session
from collections.abc import Generator
from httpx import ASGITransport, AsyncClient
from glob import glob
import os
from app.main import app
from app.core.database import engine
from app.core import database
from app.settings import image_domain


@pytest.fixture(scope="function", autouse=True)
def db() -> Generator[Session,None,None]:
    with Session(engine) as session:
        yield session
        session.rollback()
        stmt = delete(database.Image)
        session.execute(stmt)
        stmt = delete(database.User)
        session.execute(stmt)
        stmt = delete(database.Species)
        session.execute(stmt)
        stmt = delete(database.Task)
        session.execute(stmt)
        stmt = delete(database.BboxAnnotation)
        session.execute(stmt)
        stmt = delete(database.PolyAnnotation)
        session.execute(stmt)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient,None,None]:
    with TestClient(app) as c:
        yield c
    # with Client(transport=WSGITransport(app=app), base_url="http://test") as c:
    #     yield c
    # async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    #     yield c

@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    """Fixture to execute asserts before and after a test is run"""
    # Setup: fill with any logic you want
    print("Start testing")
    yield # this is where the testing happens
    images = glob(image_domain+'/test_species/*')
    for image in images:
        os.remove(image)
    # Teardown : fill with any logic you want