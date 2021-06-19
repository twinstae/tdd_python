"Batch Domain Model"

from enum import Enum
from typing import List, Optional, Set
from datetime import date
from dataclasses import dataclass

from domain import events
# class OutOfStock(Exception):
#     "할당할 수 있는 Batch가 없어요!"


@dataclass(unsafe_hash=True)
class OrderLine:
    """주문 라인"""
    orderid: str
    sku: str
    quantity: int


class AllocateResult(Enum):
    """allocate 했을 때 결과"""
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
        self._purchased_quantity = quantity
        self.eta = eta
        self._allocations: Set[OrderLine] = set()

    def __repr__(self):
        return f"<Batch {self.ref}>"

    def can_allocate(self, line: OrderLine) -> AllocateResult:
        """
        이 배치가 Line에 할당(allocate)할 수 있는지 Code로 반환. 실제로 할당하지는 않는다.
        가능한 결과는 AllocateResultCode 참조.
        """

        if line.sku != self.sku:
            return AllocateResult.DIFFRENT_SKU

        if line in self._allocations:
            return AllocateResult.ALREADY_ALLOCATED_LINE

        if self.available_quantity < line.quantity:
            return AllocateResult.AVAILABLE_LESS_TAHN_LINE

        return AllocateResult.SUCCESS

    def allocate(self, line: OrderLine) -> AllocateResult:
        """
        실제로 배치를 할당하고 성공, 실패 여부를 Code로 반환.
        가능한 결과는 AllocateResultCode 참조.
        """

        code = self.can_allocate(line)

        if code != AllocateResult.SUCCESS:
            return code

        self._allocations.add(line)

        return AllocateResult.SUCCESS

    def deallocate(self, line: OrderLine):
        "Line에 할당된 배치를 취소"
        if line in self._allocations:
            self._allocations.remove(line)

    def __eq__(self, value):
        if not isinstance(value, Batch):
            return False
        return self.ref == value.ref

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __lt__(self, other):
        return not self.__gt__(other)

    def __hash__(self):
        return hash(self.ref)

    @property
    def allocated_quantity(self) -> int:
        "할당된 quantity"
        return sum(line.quantity for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        "남은 quantity"
        return self._purchased_quantity - self.allocated_quantity


class InvalidBatchSku(Exception):
    """
    batches 중에 Product의 sku와 다른 sku를 가지고 있는 batch가 있습니다!
    """
    def __init__(self, sku: str, batch:Batch):
        self.message = f"{batch} {batch.sku} =/= Product {sku}"


class Product:
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        for batch in batches:
            if batch.sku != sku:
                raise InvalidBatchSku(sku, batch)
        
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events: List[events.Event] = []

    def allocate(self, line: OrderLine) -> Optional[str]:
        """
        주어진 batches 중에서 can_allocate하고 eta가 가장 빠른 값에 line을 할당하고, 해당 batch.ref를 반환.
        """

        try:
            batch = next(
                b for b in sorted(self.batches)
                if b.can_allocate(line) == AllocateResult.SUCCESS
            )
            batch.allocate(line)
            self.version_number += 1
            return batch.ref
        except StopIteration:
            self.events.append(events.OutOfStock(line.sku))
            return None
            # raise OutOfStock(f"sku {line.sku} 의 재고가 없어요.") from no_next_e
