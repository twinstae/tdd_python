"""api e2e test"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from allocation.service_layer.handlers import InvalidSku
from allocation.fastapi_app import app, OrderLineDto
from allocation.adapters.orm import metadata
from allocation import config

from tests.util import random_batchref, random_sku, random_orderid

@pytest.fixture(scope="session")
def sqlite_db():
    engine = create_engine(config.get_sqlite_uri())
    metadata.create_all(engine)
    return engine


with TestClient(app) as client:

    def post_to_add_batch(ref, sku, quantity, eta):
        "/add_batch 에 요청을 날리면 batch가 추가되고 201 을 결과로 받는다."
        r = client.post(
            "/add_batch", json={"ref": ref, "sku": sku, "quantity": quantity, "eta": eta}
        )
        assert r.status_code == 201


    @pytest.mark.usefixtures("sqlite_db")
    def test_api_returns_allocation():
        """
        /allocate 에
        order data를 body로 요청하면
        status_code 는 201 created 이고
        할당한 batch.ref 를 반환한다.
        """
        sku, othersku = random_sku(), random_sku("other")  #(1)
        earlybatch = random_batchref(1)
        laterbatch = random_batchref(2)
        otherbatch = random_batchref(3)

        post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
        post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
        post_to_add_batch(otherbatch, othersku, 100, None)

        data = OrderLineDto(
           orderid=random_orderid(),
           sku=sku,
           quantity=3
        ).dict()

        res = client.post(f"/allocate", json=data)

        assert res.status_code == 201
        assert res.json()["batchref"] == earlybatch


    @pytest.mark.usefixtures("sqlite_db")
    def test_unhappy_path_returns_400_and_error_message():
        unknown_sku, orderid = random_sku(), random_orderid()

        data = {"orderid": orderid, "sku": unknown_sku, "quantity": 20}
        r = client.post("/allocate", json=data)
        assert r.status_code == 400
        assert r.json()["message"] == (InvalidSku.template % unknown_sku)
