"Batch Domain Model"

from enum import Enum
from typing import List, Optional, Set
from datetime import date
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class OrderLine:
    "주문 라인"
    orderid: str
    sku: str
    quantity: int


class AllocateResultCode(Enum):
    "allocate 했을 때 결과"
    SUCCESS = "SUCCESS"
    DIFFRENT_SKU = "Batch와 Line의 SKU가 달라요."
    ALREADY_ALLOCATED_LINE = "이미 할당된 주문이에요!"
    AVAILABLE_LESS_TAHN_LINE = "재고가 부족해서 할당할 수 없어요."


class Batch:
    """
    상품 Batch
    ref : 식별자
    sku : 가구 품목의 종류와 단위
    quantity : 가구의 수량
    eta : 예상 도착 날짜. 이미 stock에 들어 있으면 None

    _allocate : 할당된 Line들의 식별자 Set
    """

    def __init__(self, ref: str, sku: str, quantity: int, eta: Optional[date]):
        self.ref = ref
        self.sku = sku
        self.quantity = quantity
        self.eta = eta
        self._allocate: Set[OrderLine] = set()

    def can_allocate(self, line: OrderLine) -> AllocateResultCode:
        """
        이 배치가 Line에 할당(allocate)할 수 있는지 Code로 반환. 실제로 할당하지는 않는다.
        가능한 결과는 AllocateResultCode 참조.
        """

        if line.sku != self.sku:
            return AllocateResultCode.DIFFRENT_SKU

        if line in self._allocate:
            return AllocateResultCode.ALREADY_ALLOCATED_LINE

        if self.quantity < line.quantity:
            return AllocateResultCode.AVAILABLE_LESS_TAHN_LINE

        return AllocateResultCode.SUCCESS

    def allocate(self, line: OrderLine) -> AllocateResultCode:
        """
        실제로 배치를 할당하고 성공, 실패 여부를 Code로 반환.
        가능한 결과는 AllocateResultCode 참조.
        """

        code = self.can_allocate(line)

        if code != AllocateResultCode.SUCCESS:
            return code

        self.quantity -= line.quantity
        self._allocate.add(line)

        return AllocateResultCode.SUCCESS

    def __eq__(self, value):
        return self.ref == value.ref

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __lt__(self, other):
        return not self.__gt__(other)


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    """
    주어진 batches 중에서 can_allocate하고 eta가 가장 빠른 값에 line을 할당하고, 해당 batch.ref를 반환.
    """
    batch = next(b for b in sorted(batches) if b.can_allocate(line))
    batch.allocate(line)
    return batch.ref
