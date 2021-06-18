"""batch allocate service test"""

import pytest
import model
import repository
import services


class FakeRepository(repository.AbstractRepository):
    """test용 in memory 컬렉션 레포지토리"""
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, ref):
        return next(b for b in self._batches if b.reference == ref)

    def list(self):
        return list(self._batches)


class FakeSession:
    """
    테스트용 가짜 세션
    """
    committed = False

    def commit(self):
        """
        fake commit 메서드
        committed 가 True로 바뀐다.
        """
        self.committed = True


def test_returns_allocation():
    """
    service.allocate에 line, repo, session을 넘기면
    line을 batch에 할당하고
    할당한 batchref를 반환한다
    """

    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    """
    service.allocate 에 존재하지 않는 sku를 가진 line을 넘기면
    InvalidSku 에러를 발생시킨다.
    """

    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    """
    service.allocate 를 실행하면,
    FakeSession의 committed는 True로 바뀐다.
    """

    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
