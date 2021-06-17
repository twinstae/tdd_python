"test db setup"

# pytest: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from db_tables import metadata
from orm import start_mappers


@pytest.fixture
def in_memory_db():
    "sqlite in memory db 엔진을 생성"
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    "sqlite in memory db 세션을 반환"
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
