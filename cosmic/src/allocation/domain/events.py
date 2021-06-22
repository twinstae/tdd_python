from dataclasses import dataclass


class Event:
    pass


@dataclass
class OutOfStock(Event):
    sku: str


LINE_ALLOCATED = "line_allocated"

@dataclass
class Allocated(Event):
    orderid: str
    sku: str
    quantity: int
    batchref: str

