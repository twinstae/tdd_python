"""batch allocate service test"""

from domain import model
import pytest
from adapters import repository
from service_layer import services, unit_of_work
from tests.util import random_sku


class FakeRepository(repository.AbstractRepository):
    """test용 in memory 컬렉션 레포지토리"""
    def __init__(self, products):
        super().__init__()
        self._products = {product.sku: product for product in products }

    def _add(self, product: model.Product):
        sku = product.sku
        # if sku in self._products:
        #    raise ProductForTheSKUAlreadyExist(sku, self._products[sku])
        self._products[sku] = product

    def _get(self, sku: str):
        return self._products.get(sku)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    RANDOM_SKU = random_sku()
    uow=FakeUnitOfWork()
    services.add_batch("b1", RANDOM_SKU, 100, None, uow=uow)

    created_product = uow.products.get(RANDOM_SKU)
    assert created_product is not None
    assert len(created_product.batches) is 1
    assert all(batch.sku == RANDOM_SKU for batch in created_product.batches)
    assert uow.committed


def test_returns_allocation():
    """
    service.allocate에 line, repo, session을 넘기면
    line을 batch에 할당하고
    할당한 batchref를 반환한다
    """
    RANDOM_SKU = random_sku()
    uow=FakeUnitOfWork()
    services.add_batch("b1", RANDOM_SKU, 100, eta=None, uow=uow)

    result = services.allocate(
            "o1", RANDOM_SKU, 10,
            uow
        )
    assert result == "b1"


def test_error_for_invalid_sku():
    """
    service.allocate 에 존재하지 않는 sku를 가진 line을 넘기면
    InvalidSku 에러를 발생시킨다.
    """
    RANDOM_SKU = random_sku()
    uow = FakeUnitOfWork()
    services.add_batch("b1", RANDOM_SKU, 100, eta=None, uow=uow)

    with pytest.raises(services.InvalidSku, match="NONEXISTENTSKU"):
        services.allocate(
            "o1", "NONEXISTENTSKU", 10,
            uow=uow
        )


def test_commits():
    """
    service.allocate 를 실행하면,
    FakeSession의 committed는 True로 바뀐다.
    """
    RANDOM_SKU = random_sku()
    uow = FakeUnitOfWork()
    services.add_batch("b1", RANDOM_SKU, 100, eta=None, uow=uow)

    services.allocate(
        "o1", RANDOM_SKU, 10,
        uow=uow
    )
    assert uow.committed
