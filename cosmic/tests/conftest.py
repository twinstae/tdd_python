"test db setup"
# pytest: disable=redefined-outer-name
import shutil
import subprocess
import time
from pathlib import Path

import pytest
import redis
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay

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
    orm.start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def in_memory_session(session_factory):
    """sqlite in memory db 세션을 반환"""
    return session_factory()


@pytest.fixture
def file_session(file_db):
    """sqlite in memory db 세션을 반환"""
    orm.start_mappers()
    yield sessionmaker(bind=file_db)
    clear_mappers()


@retry(stop=stop_after_delay(10))
def wait_for_postgres_to_come_up(engine):
    return engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(config.get_api_url())


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up():
    r = redis.Redis(**config.get_redis_host_and_port())
    return r.ping()


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    orm.start_mappers()
    yield sessionmaker(bind=postgres_db)
    clear_mappers()


@pytest.fixture
def postgres_session(postgres_session_factory):
    return postgres_session_factory()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/allocation/fastapi_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture
def restart_redis_pubsub():
    wait_for_redis_to_come_up()
    if not shutil.which("docker-compose"):
        print("skipping restart, assumes running in container")
        return
    print("subprocess run")
    subprocess.run(
        ["docker-compose", "restart", "-t", "0", "redis_pubsub"],
        check=True,
    )
