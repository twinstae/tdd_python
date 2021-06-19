from typing import Callable, Dict, List, Type
from domain import events

def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)

class Email:
    @staticmethod
    def send_mail(address: str, body: str):
        print(f"이메일. To. {address}\n {body}")

email = Email()

def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}"
    )

HandlersT = Dict[Type[events.Event], List[Callable]]

HANDLERS:HandlersT  = {
    events.OutOfStock: [send_out_of_stock_notification],
}
