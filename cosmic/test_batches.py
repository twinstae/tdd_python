"""Batch, Line 도메인 모델 테스트"""

from datetime import date

import model

AllocateResult = model.AllocateResult
allocate = model.allocate

def make_order_line_and_batch(sku: str, order_quantity, batch_quantity):
    """
    주어진 sku, order_quantity와 batch_quantity로 Line과 Batch를 만들어서 반환.

    ref는 단일한 defalt 값이고, eta는 오늘(today)로 설정.
    *주의* ref나 eta를 다르게 설정하고 싶으면 이 함수를 쓰지 말 것.
    """
    order = model.OrderLine("order-ref", sku, order_quantity)
    batch = model.Batch("batch-ref", sku, batch_quantity, date.today())
    return order, batch


def test_buy_2_small_table():
    """
    20개가 있는 배치에서 2개 짜리 라인에 할당하면
    SUCCESS 코드를 반환하고
    18개가 남는다.
    """
    order, batch = make_order_line_and_batch(
            "SMALL_TABLE",
            order_quantity=2,
            batch_quantity=20
        )
    code = batch.allocate(order)

    assert code == AllocateResult.SUCCESS
    assert batch.available_quantity == 18


def test_available_batch_less_than_line():
    """
    1개가 있는 배치에서 2개 짜리 라인에 할당하면
    AVAILABLE_LESS_TAHN_LINE 실패 코드를 반환하고
    그대로 1개다.
    """
    order, batch = make_order_line_and_batch(
            "BLUE_CUSHION",
            order_quantity=2,
            batch_quantity=1
        )

    code = batch.allocate(order)

    assert code == AllocateResult.AVAILABLE_LESS_TAHN_LINE
    assert batch.available_quantity == 1


def test_cant_allocate_same_line_twice():
    """
    같은 배치에서 같은 라인에 두 번 할당하면
    ALREADY_ALLOCATED_LINE 실패 코드를 반환하고
    Batch에 남은 quantity 는 그대로 변하지 않는다.
    """
    order, batch = make_order_line_and_batch("BLUE_VASE", 2, 20)
    code = batch.allocate(order)

    assert code == AllocateResult.SUCCESS
    assert batch.available_quantity == 18

    code_2 = batch.allocate(order)

    assert code_2 == AllocateResult.ALREADY_ALLOCATED_LINE
    assert batch.available_quantity == 18


def test_cant_allocate_different_sku():
    """
    SKU 종류가 다른 라인에 할당하면
    DIFFRENT_SKU 에러를 반환하고
    quantity는 그대로 변하지 않는다.
    """
    order = model.OrderLine("line-4", "BLUE_VASE", 2)
    batch = model.Batch(ref="batch-4", sku="BLUE_CUSHION", quantity=10, eta=date.today())

    code = batch.allocate(order)

    assert code == AllocateResult.DIFFRENT_SKU
    assert batch.available_quantity == 10

def test_deallocate():
    """
    allocate한 라인을 deallocate하면
    quantity는 다시 원상태로 돌아온다.
    """
    order, batch = make_order_line_and_batch("BLUE_VASE", 2, 20)

    assert batch.allocate(order) == AllocateResult.SUCCESS
    assert batch.available_quantity == 18

    batch.deallocate(order)
    assert batch.available_quantity == 20


def test_can_only_deallocate_allocated_lines():
    unallocated_line, batch = make_order_line_and_batch("DECORATIVE-TRINKET", 2, 20)
    assert batch.available_quantity == 20
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20

