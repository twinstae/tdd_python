"DB 레포지토리"

import abc
from typing import List
import model


class AbstractRepository(abc.ABC):
    """
    Batch 레포지토리 추상 클래스
    """
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        """
        input : batch 모델을 받으면
        output: 없음
        side effect : db에 추가하고 영속한다.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, ref) -> model.Batch:
        """
        외부 상태 : DB 상태
        input  : Batch의 ref
        output : 해당 ref를 가진 Batch를 DB에서 꺼내서 반환한다.
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def list(self) -> List[model.Batch]:
        """
        외부 상태 : DB 상태
        input  : 없음
        output : 모든 Batch를 DB에서 꺼내서 List로 반환한다.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    "Batch 레포지토리의 SQLAlchemy 구현"
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, ref):
        return self.session.query(model.Batch).filter_by(ref=ref).one()

    def list(self):
        return self.session.query(model.Batch).all()

