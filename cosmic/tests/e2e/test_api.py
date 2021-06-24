"""api e2e test"""

import pytest

from allocation.service_layer.handlers import InvalidSku

from tests.util import random_batchref, random_sku, random_orderid
from tests.e2e import api_client


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
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

    api_client.post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    api_client.post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    api_client.post_to_add_batch(otherbatch, othersku, 100, None)

    order_id = random_orderid()

    res = api_client.post_to_allocate(order_id, sku, quantity=3)

    assert res.status_code == 202

    res = api_client.get_allocation(order_id)
    assert res.ok
    assert res.json() == [
        {"sku": sku, "batchref": earlybatch},
    ]


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()

    res = api_client.post_to_allocate(
        orderid,
        unknown_sku,
        quantity=20,
        expect_success=False,
    )

    assert res.status_code == 400
    assert res.json()["message"] == (InvalidSku.template % unknown_sku)

    res = api_client.get_allocation(orderid)
    assert res.status_code == 404
