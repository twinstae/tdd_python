"""batch service"""

from __future__ import annotations
from datetime import date
from service_layer.unit_of_work import AbstractUnitOfWork
from typing import List, Optional

from domain import model
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
    """sku가 batches 중에 없습니다."""


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
        uow.batches.add(model.Batch(ref=ref, sku=sku, quantity=quantity, eta=eta))
        uow.commit()


def allocate(
        orderid: str,
        sku: str,
        quantity: int,
        uow: AbstractUnitOfWork,
    ) -> str:
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
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = model.allocate(line, batches)
        uow.commit()
    return batchref
