"""DB 레포지토리"""

import abc
from typing import Optional, Set
from allocation.domain import model
from allocation.adapters import orm


class AbstractRepository(abc.ABC):
    """
    Batch 레포지토리 추상 클래스
    """

    def __init__(self):
        self.seen: Set[model.Product] = set()

    def add(self, product: model.Product):
        self._add(product)
        self.seen.add(product)

    def get(self, sku: str):
        product = self._get(sku=sku)
        if product:
            self.seen.add(product)
            product.events = []
        return product

    def get_by_batchref(self, batch_ref: str) -> Optional[model.Product]:
        product = self._get_by_batchref(batch_ref)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _add(self, product: model.Product):
        """
        input : product 모델을 받으면
        output: 없음
        side effect : db에 추가하고 영속한다.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> Optional[model.Product]:
        """
        외부 상태 : DB 상태
        input  : product의 sku
        output : 해당 sku를 담당하는 Product를 DB에서 꺼내서 반환한다.
        """
        raise NotImplementedError


    @abc.abstractmethod
    def _get_by_batchref(self, batchref) -> Optional[model.Product]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """Batch 레포지토리의 SQLAlchemy 구현"""
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product: model.Product):
        self.session.add(product)

    def _get(self, sku: str):
        return self.session.query(model.Product).filter_by(sku=sku).first()

    def _get_by_batchref(self, batchref: str) -> Optional[model.Product]:
        return (
            self.session.query(model.Product)
            .join(model.Batch)
            .filter(orm.batches.c.ref == batchref)
            .first()
        )
