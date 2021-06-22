from __future__ import annotations
from fastapi.logger import logger
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING

from allocation.domain import commands, events
from allocation.service_layer import handlers, unit_of_work

if TYPE_CHECKING:
    from . import unit_of_work


Message = Union[commands.Command, events.Event]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        try:
            message = queue.pop(0)
        except Exception as e:
            print(e)
            raise e
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            print(f"{message} was not an Event or Command")
            raise Exception(f"{message} was not an Event or Command")
    return results


def handle_event(
    event: events.Event,
    quene: List[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug("handling event %s with handler %s", event, handler)
            handler(event, uow=uow)
            quene.extend(uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling event %s", event)
            continue


def handle_command(
    command: commands.Command,
    queue: List[Message],
    uow: unit_of_work.AbstractUnitOfWork,
):
    logger.debug("handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise


EventHandlersT = Dict[Type[events.Event], List[Callable]]
EVENT_HANDLERS: EventHandlersT  = {
    events.Allocated: [handlers.publish_allocated_event],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}


CommandHandlersT = Dict[Type[commands.Command], Callable]
COMMAND_HANDLERS: CommandHandlersT  = {
    commands.CreateBatch: handlers.add_batch,
    commands.Allocate: handlers.allocate,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}
