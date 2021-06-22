from datetime import date
from typing import Optional
from dataclasses import dataclass


class Command:
    pass


@dataclass
class Allocate(Command):
    orderid: str
    sku: str
    quantity: int


@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    quantity: int
    eta: Optional[date] = None

CHANGE_BATCH_QUANTITY = "change_batch_quantity"

@dataclass
class ChangeBatchQuantity(Command):
    ref: str
    quantity: int
