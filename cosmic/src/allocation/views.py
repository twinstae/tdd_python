from allocation.service_layer import unit_of_work


def allocations(order_id: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            """
            SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid
            """,
            dict(orderid=order_id),
        )
    return [dict(r) for r in results] 
