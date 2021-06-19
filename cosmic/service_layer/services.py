"""batch service"""

from __future__ import annotations
from datetime import date
from service_layer.unit_of_work import AbstractUnitOfWork
from typing import List, Optional

from domain import model
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
    """sku가 batches 중에 없습니다."""
    template = "sku %s를 가진 Product가 없습니다."
    def __init__(self, sku: str) -> None:
        self.message = self.template % sku
    def __repr__(self) -> str:
        return self.message
    def __str__(self) -> str:
        return self.message


def is_valid_sku(sku: str, batches: List[model.Batch]):
    """
    input으로 받은 sku가 batches 중에 있는지 검사.
    """
    return sku in { b.sku for b in batches }


def add_batch(
        ref: str, sku: str, quantity: int, eta: Optional[date],
        uow: AbstractUnitOfWork,
    ) -> None:
    with uow:
        product = uow.products.get(sku)
        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)

        product.batches.append(model.Batch(ref=ref, sku=sku, quantity=quantity, eta=eta))
        uow.commit()


def allocate(
        orderid: str,
        sku: str,
        quantity: int,
        uow: AbstractUnitOfWork,
    ) -> Optional[str]:
    """
    input으로 받은 line을
    repo의 batches 중 하나에 할당하고 (영속)
    할당한 batchref를 반환한다.

    에러
    - InvalidSku
    - OutOfStock
    """
    line = model.OrderLine(orderid, sku, quantity)
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            raise InvalidSku(sku)
        batchref = product.allocate(line)
        uow.commit()
    return batchref
