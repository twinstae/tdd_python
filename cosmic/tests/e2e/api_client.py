from typing import Optional

import requests

from allocation import config


def post_to_add_batch(ref: str, sku: str, quantity: int, eta: Optional[str]):
    url = config.get_api_url()
    r = requests.post(f"{url}/add_batch", json={"ref": ref, "sku": sku, "quantity": quantity, "eta": eta}
    )
    assert r.status_code == 201


def post_to_allocate(orderid: str, sku: str, quantity: int, expect_success=True):
    url = config.get_api_url()

    r = requests.post(
        f"{url}/allocate",
        json={
            "orderid": orderid,
            "sku": sku,
            "quantity": quantity,
        },
    )
    if expect_success:
        assert r.status_code == 201
    return r
