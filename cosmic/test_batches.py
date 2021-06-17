"Batch, Line 도메인 모델 테스트"

from datetime import date, timedelta
import model

AllocateResultCode = model.AllocateResultCode
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

    assert code == AllocateResultCode.SUCCESS
    assert batch.quantity == 18


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

    assert code == AllocateResultCode.AVAILABLE_LESS_TAHN_LINE
    assert batch.quantity == 1


def test_cant_allocate_same_line_twice():
    """
    같은 배치에서 같은 라인에 두 번 할당하면
    ALREADY_ALLOCATED_LINE 실패 코드를 반환하고
    Batch에 남은 quantity 는 그대로 변하지 않는다.
    """
    order, batch = make_order_line_and_batch("BLUE_VASE", 2, 20)
    code = batch.allocate(order)

    assert code == AllocateResultCode.SUCCESS
    assert batch.quantity == 18

    code_2 = batch.allocate(order)

    assert code_2 == AllocateResultCode.ALREADY_ALLOCATED_LINE
    assert batch.quantity == 18


def test_cant_allocate_different_sku():
    """
    SKU 종류가 다른 라인에 할당하면
    DIFFRENT_SKU 에러를 반환하고
    quantity는 그대로 변하지 않는다.
    """
    order = model.OrderLine("line-4", "BLUE_VASE", 2)
    batch = model.Batch(ref="batch-4", sku="BLUE_CUSHION", quantity=10, eta=date.today())

    code = batch.allocate(order)

    assert code == AllocateResultCode.DIFFRENT_SKU
    assert batch.quantity == 10


today = date.today()
tomorrow = date.today() + timedelta(days=1)
later = date.today() + timedelta(days=7)


def test_prefers_current_stock_batches_to_shipments():
    """
    allocate 함수로 여러 배치 중에 하나에 할당하면
    eta가 없는 in-stock-batch에 할당한다.
    """
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = model.OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.quantity == 90
    assert shipment_batch.quantity == 100


def test_prefers_earlier_batches():
    """
    여러 배치에 allocate 함수로 할당하는데
    allocate 함수로 여러 배치 중에 하나에 할당하면
    in_stock_batch가 없으면
    가장 빠른 earliest 배치에 할당한다.
    """
    earliest = model.Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = model.Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = model.Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = model.OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.quantity == 90
    assert medium.quantity == 100
    assert latest.quantity == 100


def test_returns_allocated_batch_ref():
    """
    allocate 함수는 할당한 배치의 ref를 반환한다.
    """
    in_stock_batch = model.Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = model.OrderLine("oref", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.ref
