"test db setup"

# pytest: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.exc import ArgumentError

from allocation.adapters import orm
from allocation.adapters.orm import metadata
from allocation import config

@pytest.fixture
def in_memory_db():
    """sqlite in memory db 엔진을 생성"""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def file_db():
    """sqlite file db 엔진을 생성"""
    engine = create_engine(config.get_sqlite_uri)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    try:
        orm.start_mappers()
    except ArgumentError:
        pass
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def in_memory_session(session_factory):
    """sqlite in memory db 세션을 반환"""
    return session_factory()


@pytest.fixture
def file_session(file_db):
    """sqlite in memory db 세션을 반환"""
    try:
        orm.start_mappers()
    except ArgumentError:
        pass
    yield sessionmaker(bind=file_db)
    clear_mappers()

