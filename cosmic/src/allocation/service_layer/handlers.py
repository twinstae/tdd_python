from __future__ import annotations
from dataclasses import asdict
from typing import Optional, List, Dict, Callable, Type, TYPE_CHECKING

from allocation.domain import commands, events, model
from allocation.adapters import redis_event_publisher

if TYPE_CHECKING:
    from . import unit_of_work


class InvalidSku(Exception):
    """sku가 batches 중에 없습니다."""
    template = "sku %s를 가진 Product가 없습니다."
    def __init__(self, sku: str) -> None:
        self.message = self.template % sku
    def __repr__(self) -> str:
        return self.message
    def __str__(self) -> str:
        return self.message


def is_valid_sku(sku: str, batches: List[model.Batch]):
    """
    input으로 받은 sku가 batches 중에 있는지 검사.
    """
    return sku in { b.sku for b in batches }


def add_batch(
    cmd: commands.CreateBatch,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get(cmd.sku)
        if product is None:
            product = model.Product(cmd.sku, batches=[])
            uow.products.add(product)

        product.batches.append(model.Batch(ref=cmd.ref, sku=cmd.sku, quantity=cmd.quantity, eta=cmd.eta))
        uow.commit()


def allocate(
    cmd: commands.Allocate,
    uow: unit_of_work.AbstractUnitOfWork,
) -> Optional[str]:
    """
    input으로 받은 line을
    repo의 batches 중 하나에 할당하고 (영속)
    할당한 batchref를 반환한다.

    에러
    - InvalidSku
    - OutOfStock
    """
    line = model.OrderLine(cmd.orderid, cmd.sku, cmd.quantity)
    with uow:
        product = uow.products.get(sku=cmd.sku)
        if product is None:
            raise InvalidSku(cmd.sku)
        batchref = product.allocate(line)
        uow.commit()
        return batchref


def change_batch_quantity(
    cmd: commands.ChangeBatchQuantity,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get_by_batchref(batch_ref=cmd.ref)
        product.change_batch_quantity(ref=cmd.ref, quantity=cmd.quantity)
        uow.commit()


class Email:
    @staticmethod
    def send(address: str, body: str):
        print(f"이메일. To. {address}\n {body}")

email = Email()

def send_out_of_stock_notification(event: events.OutOfStock, uow):
    email.send(
        "stock@made.com",
        f"Out of stock for {event.sku}"
    )

def publish_allocated_event(
    event: events.Allocated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    redis_event_publisher.publish(events.LINE_ALLOCATED, event)


def add_allocation_to_read_model(
    event: events.Allocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            INSERT INTO allocations_view (orderid, sku, batchref)
            VALUES (:orderid, :sku, :batchref)
            """,
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref),
        )
        uow.commit()


def reallocate(
    event: events.Deallocated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    allocate(commands.Allocate(**asdict(event)), uow=uow)


def remove_allocation_from_read_model(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            DELETE FROM allocations_view
            WHERE orderid = :orderid AND sku = :sku
            """,
            dict(orderid=event.orderid, sku=event.sku),
        )
        uow.commit()


EventHandlersT = Dict[Type[events.Event], List[Callable]]
EVENT_HANDLERS: EventHandlersT  = {
    events.Allocated: [publish_allocated_event, add_allocation_to_read_model],
    events.Deallocated: [remove_allocation_from_read_model, reallocate],
    events.OutOfStock: [send_out_of_stock_notification],
}


CommandHandlersT = Dict[Type[commands.Command], Callable]
COMMAND_HANDLERS: CommandHandlersT  = {
    commands.CreateBatch: add_batch,
    commands.Allocate: allocate,
    commands.ChangeBatchQuantity: change_batch_quantity,
}
