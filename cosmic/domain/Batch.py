from enum import Enum
from typing import List, Optional
from datetime import date
from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    ref: str
    sku: str
    quantity: int


class AllocateResultCode(Enum):
    SUCCESS = "SUCCESS"
    DIFFRENT_SKU = "Batch와 Line의 SKU가 달라요." 
    ALREADY_ALLOCATED_LINE = "이미 할당된 주문이에요!"
    AVAILABLE_LESS_TAHN_LINE = "재고가 부족해서 할당할 수 없어요."


class Batch:

    def __init__(self, ref: str, sku: str, quantity: int, eta: Optional[date]):
        self.ref = ref
        self.sku = sku
        self.quantity = quantity
        self.eta = eta
        self._allocate = set()

    def can_allocate(self, line):
        if line.sku != self.sku:
            return AllocateResultCode.DIFFRENT_SKU

        if line.ref in self._allocate:
            return AllocateResultCode.ALREADY_ALLOCATED_LINE                   

        if self.quantity < line.quantity:
            return AllocateResultCode.AVAILABLE_LESS_TAHN_LINE

        return AllocateResultCode.SUCCESS

    def allocate(self, line: Line) -> AllocateResultCode:
        code = self.can_allocate(line)

        if code != AllocateResultCode.SUCCESS:
            return code

        self.quantity -= line.quantity
        self._allocate.add(line.ref)

        return AllocateResultCode.SUCCESS


    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


def allocate(line: Line, batches: List[Batch]) -> str:
    batch = next(b for b in sorted(batches) if b.can_allocate(line))
    batch.allocate(line)
    return batch.ref



