"""batch service"""

from __future__ import annotations
from typing import List

import model
from model import OrderLine, Batch
from repository import AbstractRepository


class InvalidSku(Exception):
    """sku가 batches 중에 없습니다."""


def is_valid_sku(sku: str, batches: List[Batch]):
    """
    input으로 받은 sku가 batches 중에 있는지 검사.
    """
    return sku in { b.sku for b in batches }


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    """
    input으로 받은 line을
    repo의 batches 중 하나에 할당하고 (영속)
    할당한 batchref를 반환한다.

    에러
    - InvalidSku
    - OutOfStock
    """
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
