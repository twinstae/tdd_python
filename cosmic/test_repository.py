"""repository 테스트"""

import model
import repository

def test_repository_can_save_a_batch(in_memory_session):
    """
    batch를 레포지토리에 저장하면
    DB에서 똑같은 배치를 복원할 수 있다.
    """
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(in_memory_session)
    repo.add(batch)  #(1)
    in_memory_session.commit()  #(2)

    rows = in_memory_session.execute(  #(3)
        'SELECT ref, sku, _purchased_quantity, eta FROM "batches"'
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(in_memory_session):
    """OrderLine(order1, \"GENERIC-SOFA\", 12)를 db에 추가한다."""

    in_memory_session.execute(  #(1)
        "INSERT INTO order_lines (orderid, sku, quantity)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )
    [[orderline_id]] = in_memory_session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(in_memory_session, batch_id):
    """주어진 Batch(:batch_id, GENERIC-SOFA 100, eta=None)을 db에 추가한다."""
    in_memory_session.execute(  #(1)
        "INSERT INTO batches (ref, sku, _purchased_quantity, eta)"
        ' VALUES (:ref, "GENERIC-SOFA", 100, null)',
        dict(ref=batch_id)
    )
    [[batch_id]] = in_memory_session.execute(
        'SELECT id FROM batches WHERE ref=:batch_id AND sku="GENERIC-SOFA"',
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(in_memory_session, orderline_id, batch_id):
    """주어진 orderline_id를 batch_id에 할당한 allocation을 db에 추가한다."""
    in_memory_session.execute(
        "INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(in_memory_session):
    """repository는 db에서 batch를 allocations와 같이 가져올 수 있어야 한다."""

    orderline_id = insert_order_line(in_memory_session)
    batch1_id = insert_batch(in_memory_session, "batch1")
    insert_batch(in_memory_session, "batch2")
    insert_allocation(in_memory_session, orderline_id, batch1_id)  #(2)

    repo = repository.SqlAlchemyRepository(in_memory_session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference  #(3)
    assert retrieved.sku == expected.sku  #(4)
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {  #(4)
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
