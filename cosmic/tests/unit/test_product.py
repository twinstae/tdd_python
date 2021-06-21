import pytest

from allocation.domain import events
from allocation.domain.model import Batch, OrderLine, Product
from tests.util import random_sku, today, tomorrow, later


def test_prefers_current_stock_batches_to_shipments():
    """
    allocate 함수로 여러 배치 중에 하나에 할당하면
    eta가 없는 in-stock-batch에 할당한다.
    """
    RETRO_CLOCK = "RETRO-CLOCK"
    in_stock_batch = Batch("in-stock-batch", RETRO_CLOCK, 100, eta=None)
    shipment_batch = Batch("shipment-batch", RETRO_CLOCK, 100, eta=tomorrow)
    product = Product(sku=RETRO_CLOCK, batches=[in_stock_batch, shipment_batch])

    line = OrderLine("oref", RETRO_CLOCK, 10)

    product.allocate(line)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    """
    여러 배치에 allocate 함수로 할당하는데
    allocate 함수로 여러 배치 중에 하나에 할당하면
    in_stock_batch가 없으면
    가장 빠른 earliest 배치에 할당한다.
    """
    MINIMALIST_SPOON = "MINIMALIST-SPOON"
    earliest = Batch("speedy-batch", MINIMALIST_SPOON, 100, eta=today)
    medium = Batch("normal-batch", MINIMALIST_SPOON, 100, eta=tomorrow)
    latest = Batch("slow-batch", MINIMALIST_SPOON, 100, eta=later)
    product = Product(sku=MINIMALIST_SPOON, batches=[earliest, medium, latest])

    line = OrderLine("order1", MINIMALIST_SPOON, 10)

    product.allocate(line)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    """
    allocate 함수는 할당한 배치의 ref를 반환한다.
    """
    HIGHBROW_POSTER = "HIGHBROW-POSTER"
    in_stock_batch = Batch("in-stock-batch-ref", HIGHBROW_POSTER, 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", HIGHBROW_POSTER, 100, eta=tomorrow)
    product = Product(sku=HIGHBROW_POSTER, batches=[in_stock_batch, shipment_batch])

    line = OrderLine("oref", HIGHBROW_POSTER, 10)

    allocation = product.allocate(line)

    assert allocation == in_stock_batch.ref


def test_records_out_of_stock_event_if_cannot_allocate():
    """
    allocate했을 때 할당할 batch가 없으면
    Product.events에 OutOfStock Event가 추가된다.
    """
    RANDOM_SKU = random_sku()
    ALL_QUANTITY = 10
    batch = Batch("batch1", RANDOM_SKU, ALL_QUANTITY, eta=today)
    product = Product(sku=RANDOM_SKU, batches=[batch])
    product.allocate(OrderLine("order1", RANDOM_SKU, ALL_QUANTITY))

    allocation = product.allocate(OrderLine("order2", RANDOM_SKU, 1000))
    assert product.events[-1] == events.OutOfStock(sku=RANDOM_SKU)
    assert allocation is None
