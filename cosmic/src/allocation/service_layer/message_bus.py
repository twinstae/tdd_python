from __future__ import annotations
from fastapi.logger import logger
from typing import Union, TYPE_CHECKING

from allocation.domain import commands, events
from allocation.service_layer import handlers, unit_of_work

if TYPE_CHECKING:
    from . import unit_of_work


Message = Union[commands.Command, events.Event]

class MessageBus:
    def __init__(
        self,
        uow: unit_of_work.AbstractUnitOfWork,
        event_handlers: handlers.EventHandlersT,
        command_handlers: handlers.CommandHandlersT,
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers


    def handle(self, message: Message):
        results = []
        self.queue = [message]
        while self.queue:
            try:
                message = self.queue.pop(0)
            except Exception as e:
                print(e)
                raise e
            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                cmd_result = self.handle_command(message)
                results.append(cmd_result)
            else:
                print(f"{message} was not an Event or Command")
                raise Exception(f"{message} was not an Event or Command")
        return results


    def handle_event(
        self,
        event: events.Event,
    ):
        for handler in handlers.EVENT_HANDLERS[type(event)]:
            try:
                logger.debug("handling event %s with handler %s", event, handler)
                handler(event, uow=self.uow)
                self.queue.extend(self.uow.collect_new_events())
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue


    def handle_command(
        self,
        command: commands.Command,
    ):
        logger.debug("handling command %s", command)
        try:
            handler = handlers.COMMAND_HANDLERS[type(command)]
            result = handler(command, uow=self.uow)
            self.queue.extend(self.uow.collect_new_events())
            return result
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
