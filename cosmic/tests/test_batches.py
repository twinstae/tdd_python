from collections import namedtuple
from enum import Enum
from typing import List, Optional, Tuple
from datetime import date, timedelta
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


def make_order_line_and_batch(sku: str, order_quantity, batch_quantity):
    order = Line("order-ref", sku, order_quantity)
    batch = Batch("batch-ref", sku, batch_quantity, date.today())   
    return order, batch


def test_buy_2_small_table():
    order, batch = make_order_line_and_batch(
            "SMALL_TABLE",
            order_quantity=2,
            batch_quantity=20
        )
    code = batch.allocate(order)

    assert code == AllocateResultCode.SUCCESS
    assert batch.quantity == 18


def test_available_batch_less_than_line():
    order, batch = make_order_line_and_batch(
            "BLUE_CUSHION",
            order_quantity=2,
            batch_quantity=1
        )

    code = batch.allocate(order)

    assert code == AllocateResultCode.AVAILABLE_LESS_TAHN_LINE
    assert batch.quantity == 1


def test_cant_allocate_same_line_twice():
    order, batch = make_order_line_and_batch("BLUE_VASE", 2, 20)
    code = batch.allocate(order)

    assert code == AllocateResultCode.SUCCESS
    assert batch.quantity == 18

    code_2 = batch.allocate(order)

    assert code_2 == AllocateResultCode.ALREADY_ALLOCATED_LINE
    assert batch.quantity == 18


def test_cant_allocate_different_sku():
    order = Line("line-4", "BLUE_VASE", 2)
    batch = Batch(ref="batch-4", sku="BLUE_CUSHION", quantity=10, eta=date.today())

    code = batch.allocate(order)

    assert code == AllocateResultCode.DIFFRENT_SKU


today = date.today()
tomorrow = date.today() + timedelta(days=1)
later = date.today() + timedelta(days=7)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = Line("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.quantity == 90
    assert shipment_batch.quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = Line("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.quantity == 90
    assert medium.quantity == 100
    assert latest.quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = Line("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.ref
