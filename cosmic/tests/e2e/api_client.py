from typing import Optional

import requests

from allocation import config

url = config.get_api_url()

def post_to_add_batch(ref: str, sku: str, quantity: int, eta: Optional[str]):
    res = requests.post(f"{url}/add_batch", json={"ref": ref, "sku": sku, "quantity": quantity, "eta": eta}
    )
    assert res.status_code == 201


def post_to_allocate(orderid: str, sku: str, quantity: int, expect_success=True):
    res = requests.post(
        f"{url}/allocate",
        json={
            "orderid": orderid,
            "sku": sku,
            "quantity": quantity,
        },
    )
    if expect_success:
        assert res.status_code == 202
    return res


def get_allocation(order_id: str):
    return requests.get(f"{url}/allocations/{order_id}")
