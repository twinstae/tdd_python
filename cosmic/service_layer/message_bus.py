from __future__ import annotations
import logging
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING
from domain import commands, events
from service_layer import handlers, unit_of_work


if TYPE_CHECKING:
    from . import unit_of_work


logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
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
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}


CommandHandlersT = Dict[Type[commands.Command], Callable]
COMMAND_HANDLERS: CommandHandlersT  = {
    commands.CreateBatch: handlers.add_batch,
    commands.Allocate: handlers.allocate,
}
