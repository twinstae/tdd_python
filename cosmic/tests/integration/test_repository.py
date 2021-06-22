from allocation.adapters import repository
from allocation.domain import model


def test_get_by_batchref(in_memory_session):
    repo = repository.SqlAlchemyRepository(in_memory_session)
    b1 = model.Batch(ref="b1", sku="sku1", quantity=100, eta=None)
    b2 = model.Batch(ref="b2", sku="sku1", quantity=100, eta=None)
    b3 = model.Batch(ref="b3", sku="sku2", quantity=100, eta=None)
    p1 = model.Product(sku="sku1", batches=[b1, b2])
    p2 = model.Product(sku="sku2", batches=[b3])
    repo.add(p1)
    repo.add(p2)
    assert repo.get_by_batchref("b2") == p1
    assert repo.get_by_batchref("b3") == p2


class FakeRepository(repository.AbstractRepository):
    """test용 in memory 컬렉션 레포지토리"""
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product: model.Product):
        self._products.add(product)

    def _get(self, sku: str):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batch_ref: str):
        return next(
            (p for p in self._products for b in p.batches if b.ref == batch_ref),
            None,
        )


def test_get_by_batchref_fake_repo():
    repo = FakeRepository([])
    b1 = model.Batch(ref="b1", sku="sku1", quantity=100, eta=None)
    b2 = model.Batch(ref="b2", sku="sku1", quantity=100, eta=None)
    b3 = model.Batch(ref="b3", sku="sku2", quantity=100, eta=None)
    p1 = model.Product(sku="sku1", batches=[b1, b2])
    p2 = model.Product(sku="sku2", batches=[b3])
    repo.add(p1)
    repo.add(p2)
    assert repo.get_by_batchref("b2") == p1
    assert repo.get_by_batchref("b3") == p2
