from collections import namedtuple
from enum import Enum
from typing import Tuple
from datetime import date
from dataclasses import dataclass

class SKU(Enum):
    SMALL_TABLE = "SMALL_TABLE"
    BLUE_CUSHION = "BLUE_CUSHION"
    BLUE_VASE = "BLUE_VASE"


@dataclass(frozen=True)
class Line:
    ref: int
    sku: SKU
    quantity: int
    allocated: bool


class AllocateResultCode(Enum):
    SUCCESS = "SUCCESS"
    DIFFRENT_SKU = "Batch와 Line의 SKU가 달라요." 
    ALREADY_ALLOCATED_LINE = "이미 할당된 주문이에요!"
    AVAILABLE_LESS_TAHN_LINE = "재고가 부족해서 할당할 수 없어요."


@dataclass(frozen=True)
class Batch:
    ref: int
    sku: SKU
    quantity: int
    eta: date

    def allocate(self, line: Line) -> Tuple[AllocateResultCode, "Batch", Line]:
        if line.sku != self.sku:
            return (AllocateResultCode.DIFFRENT_SKU, self, line)

        if line.allocated:
            return (AllocateResultCode.ALREADY_ALLOCATED_LINE, self, line)                   

        if self.quantity < line.quantity:
            return (AllocateResultCode.AVAILABLE_LESS_TAHN_LINE, self, line)
        
        new_batch = Batch(
                self.ref,
                self.sku,
                quantity=self.quantity - line.quantity,
                eta=self.eta)
        allocated_line = Line(line.ref, line.sku, line.quantity, True)

        return (AllocateResultCode.SUCCESS, new_batch, allocated_line)


def make_order_line_and_batch(sku: SKU, order_quantity, batch_quantity):
    order = Line(1, sku, order_quantity, False)
    batch = Batch(1, sku, batch_quantity, date.today())   
    return order, batch


def test_buy_2_small_table():
    order, batch = make_order_line_and_batch(
            SKU.SMALL_TABLE,
            order_quantity=2,
            batch_quantity=20
        )
    code, new_batch, allocated_line = batch.allocate(order)

    assert code == AllocateResultCode.SUCCESS
    assert allocated_line.allocated == True
    assert new_batch.quantity == 18


def test_available_batch_less_than_line():
    order, batch = make_order_line_and_batch(
            SKU.BLUE_CUSHION,
            order_quantity=2,
            batch_quantity=1
        )

    code, new_batch, new_line = batch.allocate(order)

    assert code == AllocateResultCode.AVAILABLE_LESS_TAHN_LINE

    assert new_batch.quantity == 1
    assert new_line.allocated == False


def test_cant_allocate_same_line_twice():
    order, batch = make_order_line_and_batch(SKU.BLUE_VASE, 2, 20)
    code, new_batch, allocated_line = batch.allocate(order)

    assert code == AllocateResultCode.SUCCESS
    assert new_batch.quantity == 18
    assert allocated_line.allocated == True

    code_2, new_batch_2, allocated_line_2 = new_batch.allocate(allocated_line)

    assert code_2 == AllocateResultCode.ALREADY_ALLOCATED_LINE
    assert new_batch_2.quantity == 18
    assert allocated_line_2.allocated == True


def test_cant_allocate_different_sku():
    order = Line(4, SKU.BLUE_VASE, 2, False)
    batch = Batch(ref=4, sku=SKU.BLUE_CUSHION, quantity=10, eta=date.today())

    code, new_batch, new_line = batch.allocate(order)

    assert code == AllocateResultCode.DIFFRENT_SKU
    assert new_batch.quantity == batch.quantity
    assert new_line.allocated == False
