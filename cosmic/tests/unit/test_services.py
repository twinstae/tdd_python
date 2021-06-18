"""batch allocate service test"""

import pytest
from domain import model
from adapters import repository
from service_layer import services


class FakeRepository(repository.AbstractRepository):
    """test용 in memory 컬렉션 레포지토리"""
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, ref):
        return next(b for b in self._batches if b.ref == ref)

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


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_returns_allocation():
    """
    service.allocate에 line, repo, session을 넘기면
    line을 batch에 할당하고
    할당한 batchref를 반환한다
    """

    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, eta=None, repo=repo, session=session)

    result = services.allocate(
            "o1", "COMPLICATED-LAMP", 10,
            repo=repo,
            session=session
        )
    assert result == "b1"


def test_error_for_invalid_sku():
    """
    service.allocate 에 존재하지 않는 sku를 가진 line을 넘기면
    InvalidSku 에러를 발생시킨다.
    """
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, eta=None, repo=repo, session=session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(
                "o1", "NONEXISTENTSKU", 10,
                repo = repo,
                session = session
            )


def test_commits():
    """
    service.allocate 를 실행하면,
    FakeSession의 committed는 True로 바뀐다.
    """
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, eta=None, repo=repo, session=session)

    services.allocate(
            "o1", "OMINOUS-MIRROR", 10,
            repo=repo,
            session=session
        )
    assert session.committed is True
