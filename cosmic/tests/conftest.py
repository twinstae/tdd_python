"test db setup"

# pytest: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.exc import ArgumentError
from db_tables import metadata
from adapters import orm


@pytest.fixture
def in_memory_db():
    """sqlite in memory db 엔진을 생성"""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def file_db():
    """sqlite file db 엔진을 생성"""
    engine = create_engine("sqlite:///test.db")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def in_memory_session(in_memory_db):
    """sqlite in memory db 세션을 반환"""
    try:
        orm.start_mappers()
    except ArgumentError:
        pass
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


@pytest.fixture
def file_session(file_db):
    """sqlite in memory db 세션을 반환"""
    yield sessionmaker(bind=file_db)()
