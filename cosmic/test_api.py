# pylint: disable=redefined-outer-name

"api e2e test"
import pytest
import requests

import config
from util import random_batchref, random_sku, random_orderid
from fastapi_app import OrderLineDto

@pytest.fixture
def add_stock(file_session):
    "주어진 lines에 해당하는 batches를 db에 추가하는 add_stock fixture"
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, quantity, eta in lines:
            file_session.execute(
                "INSERT INTO batches (ref, sku, _purchased_quantity, eta)"
                " VALUES (:ref, :sku, :quantity, :eta)",
                dict(ref=ref, sku=sku, quantity=quantity, eta=eta),
            )
            [[batch_id]] = file_session.execute(
                "SELECT id FROM batches WHERE ref=:ref AND sku=:sku",
                dict(ref=ref, sku=sku),
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        file_session.commit()

    yield _add_stock

    for batch_id in batches_added:
        file_session.execute(
            "DELETE FROM allocations WHERE batch_id=:batch_id",
            dict(batch_id=batch_id),
        )
        file_session.execute(
            "DELETE FROM batches WHERE id=:batch_id", dict(batch_id=batch_id),
        )
    for sku in skus_added:
        file_session.execute(
            "DELETE FROM order_lines WHERE sku=:sku", dict(sku=sku),
        )
        file_session.commit()


# @pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock):
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
    add_stock(  #(2)
        [
            (laterbatch, sku, 100, "2011-01-02"),
            (earlybatch, sku, 100, "2011-01-01"),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = OrderLineDto(
            orderid=random_orderid(),
            sku=sku,
            quantity=3
        ).dict()
    url = config.get_api_url()  #(3)

    res = requests.post(f"{url}/allocate", json=data)

    assert res.status_code == 201
    assert res.json()["batchref"] == earlybatch
