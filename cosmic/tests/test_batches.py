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


class AllocateResultCode(Enum):
    SUCCESS = "SUCCESS"
    DIFFRENT_SKU = "Batch와 Line의 SKU가 달라요." 
    ALREADY_ALLOCATED_LINE = "이미 할당된 주문이에요!"
    AVAILABLE_LESS_TAHN_LINE = "재고가 부족해서 할당할 수 없어요."


class Batch:

    def __init__(self, ref: int, sku: SKU, quantity: int, eta: date):
        self.ref = ref
        self.sku = sku
        self.quantity = quantity
        self.eta = eta
        self._allocate = set()

    def allocate(self, line: Line) -> AllocateResultCode:
        if line.sku != self.sku:
            return AllocateResultCode.DIFFRENT_SKU

        if line.ref in self._allocate:
            return AllocateResultCode.ALREADY_ALLOCATED_LINE                   

        if self.quantity < line.quantity:
            return AllocateResultCode.AVAILABLE_LESS_TAHN_LINE
        
        self.quantity -= line.quantity
        self._allocate.add(line.ref)

        return AllocateResultCode.SUCCESS


def make_order_line_and_batch(sku: SKU, order_quantity, batch_quantity):
    order = Line(1, sku, order_quantity)
    batch = Batch(1, sku, batch_quantity, date.today())   
    return order, batch


def test_buy_2_small_table():
    order, batch = make_order_line_and_batch(
            SKU.SMALL_TABLE,
            order_quantity=2,
            batch_quantity=20
        )
    code = batch.allocate(order)

    assert code == AllocateResultCode.SUCCESS
    assert batch.quantity == 18


def test_available_batch_less_than_line():
    order, batch = make_order_line_and_batch(
            SKU.BLUE_CUSHION,
            order_quantity=2,
            batch_quantity=1
        )

    code = batch.allocate(order)

    assert code == AllocateResultCode.AVAILABLE_LESS_TAHN_LINE
    assert batch.quantity == 1


def test_cant_allocate_same_line_twice():
    order, batch = make_order_line_and_batch(SKU.BLUE_VASE, 2, 20)
    code = batch.allocate(order)

    assert code == AllocateResultCode.SUCCESS
    assert batch.quantity == 18

    code_2 = batch.allocate(order)

    assert code_2 == AllocateResultCode.ALREADY_ALLOCATED_LINE
    assert batch.quantity == 18


def test_cant_allocate_different_sku():
    order = Line(4, SKU.BLUE_VASE, 2)
    batch = Batch(ref=4, sku=SKU.BLUE_CUSHION, quantity=10, eta=date.today())

    code = batch.allocate(order)

    assert code == AllocateResultCode.DIFFRENT_SKU
