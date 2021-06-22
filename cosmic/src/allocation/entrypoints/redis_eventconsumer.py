import json

import redis
import logging
from allocation import config
from allocation.adapters import orm
from allocation.domain import commands
from allocation.service_layer import message_bus, unit_of_work

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())

def main():
    logging.info("Redis pubsub starting")
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(commands.CHANGE_BATCH_QUANTITY)

    for m in pubsub.listen():
        handle_change_batch_quantity(m)


def handle_change_batch_quantity(m):
    logging.info("handling %s", m)
    data = json.loads(m["data"])
    cmd = commands.ChangeBatchQuantity(ref=data["batchref"], quantity=data["quantity"])
    message_bus.handle(cmd, uow=unit_of_work.SqlAlchemyUnitOfWork())


if __name__ == "__main__":
    main()
