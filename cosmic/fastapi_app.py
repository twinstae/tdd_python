# pylint: disable=too-few-public-methods
"fastapi app"

# pylint: disable=no-name-in-module
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from fastapi import FastAPI,Body
from starlette.responses import JSONResponse

# import config
from domain import commands
from adapters import orm
from service_layer import handlers, message_bus
from service_layer.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork


# config.get_postgres_uri()))
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    orm.start_mappers()


class OrderLineDto(BaseModel):
    """OrderLine의 Pydantic 모델. 귀찮군..."""
    orderid: str
    sku: str
    quantity: int


class BatchDto(BaseModel):
    """Batch의 Pydantic 모델. 귀찮군..."""
    ref: str
    sku: str
    quantity: int
    eta: Optional[str]


@app.post("/add_batch")
def add_batch(
    body: BatchDto = Body(None),
):
    uow: AbstractUnitOfWork = SqlAlchemyUnitOfWork()

    eta = body.eta
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    cmd = commands.CreateBatch(
        ref=body.ref,
        sku=body.sku,
        quantity=body.quantity,
        eta=eta,
    )
    message_bus.handle(cmd, uow)

    return JSONResponse({"ok": True}, status_code=201)


@app.post("/allocate")
def allocate_endpoint(
    body: OrderLineDto = Body(default=None),
):
    """
    req
    - body : OrderLineDto

    res
    - 201 {"batchref": str}
    - 400 {"message": str(InvalidSku)}
    """
    uow: AbstractUnitOfWork = SqlAlchemyUnitOfWork()
    try:
        cmd = commands.Allocate(**body.dict())
        results = message_bus.handle(cmd, uow)
        batch_ref = results.pop(0)
    except (handlers.InvalidSku) as error:
        return JSONResponse({"message": str(error)}, status_code=400)

    return JSONResponse({"batchref": batch_ref}, status_code=201)
