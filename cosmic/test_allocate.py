from datetime import date, timedelta

import pytest

import model

AllocateResult = model.AllocateResult
allocate = model.allocate

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

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


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

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    """
    allocate 함수는 할당한 배치의 ref를 반환한다.
    """
    in_stock_batch = model.Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = model.OrderLine("oref", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.ref


def test_allocate_out_of_stock():
    """
    allocate 할 batch가 없으면 OutOfStock 에러를 뱉는다.
    """
    small_batch = model.Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    small_batch_2 = model.Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    large_order_line = model.OrderLine("oref", "HIGHBROW-POSTER", 1000)

    with pytest.raises(model.OutOfStock, match="HIGHBROW-POSTER"):
        allocate(large_order_line, [small_batch, small_batch_2])
