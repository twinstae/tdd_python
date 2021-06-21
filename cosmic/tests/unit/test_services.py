"""batch allocate service test"""

from collections import defaultdict

import pytest

from allocation.domain import model, commands
from allocation.adapters import repository
from allocation.service_layer import unit_of_work, message_bus, handlers
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


class FakeNotifications():
    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, destination, message):
        self.sent[destination].append(message)

class TestAddBatch:
    def test_for_new_product(self):
        RANDOM_SKU = random_sku()
        uow = FakeUnitOfWork()
        message_bus.handle(
            commands.CreateBatch("b1", RANDOM_SKU, 100, None), uow
        )
        created_product = uow.products.get(RANDOM_SKU)
        assert created_product is not None
        assert len(created_product.batches) is 1
        assert all(batch.sku == RANDOM_SKU for batch in created_product.batches)
        assert uow.committed

    def test_for_existing_product(self):
        RANDOM_SKU = random_sku()
        uow = FakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", RANDOM_SKU, 100, None), uow)
        message_bus.handle(commands.CreateBatch("b2", RANDOM_SKU, 99, None), uow)
        assert "b2" in [b.ref for b in uow.products.get(RANDOM_SKU).batches]

class TestAllocate:
    def test_allocates(self):
        uow = FakeUnitOfWork()
        message_bus.handle(
            commands.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None), uow
        )
        results = message_bus.handle(
            commands.Allocate("o1", "COMPLICATED-LAMP", 10), uow
        )
        assert results.pop(0) == "batch1"
        [batch] = uow.products.get("COMPLICATED-LAMP").batches
        assert batch.available_quantity == 90

    def test_errors_for_invalid_sku(self):
        uow = FakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", "AREALSKU", 100, None), uow)

        expected = handlers.InvalidSku.template % "NONEXISTENTSKU"
        with pytest.raises(handlers.InvalidSku, match=expected):
            message_bus.handle(commands.Allocate("o1", "NONEXISTENTSKU", 10), uow)

    def test_commits(self):
        uow = FakeUnitOfWork()
        message_bus.handle(
            commands.CreateBatch("b1", "OMINOUS-MIRROR", 100, None), uow
        )
        message_bus.handle(commands.Allocate("o1", "OMINOUS-MIRROR", 10), uow)
        assert uow.committed

    @pytest.mark.skip("TODO: notification 구현")
    def test_sends_email_on_out_of_stock_error(self):
        fake_notifs = FakeNotifications()
        uow = FakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", "POPULAR-CURTAINS", 9, None), uow)
        message_bus.handle(commands.Allocate("o1", "POPULAR-CURTAINS", 10), uow)

        assert fake_notifs.sent["stock@made.com"] == [
            f"Out of stock for POPULAR-CURTAINS",
        ]
