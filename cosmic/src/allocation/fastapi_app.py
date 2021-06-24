# pylint: disable=too-few-public-methods
"fastapi app"

# pylint: disable=no-name-in-module
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from fastapi import FastAPI, Body
from fastapi.logger import logger
from starlette.responses import JSONResponse

from allocation import bootstrap, views
from allocation.domain import commands
from allocation.adapters import orm
from allocation.service_layer import handlers

app = FastAPI()
bus = bootstrap.bootstrap()

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
    eta = body.eta
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    cmd = commands.CreateBatch(
        ref=body.ref,
        sku=body.sku,
        quantity=body.quantity,
        eta=eta,
    )
    bus.handle(cmd)

    return JSONResponse({"ok": True}, status_code=201)


@app.post("/allocate")
def allocate_endpoint(
    body: OrderLineDto = Body(default=None),
):
    """
    req
    - body : OrderLineDto

    res
    - 202 {"batchref": str}
    - 400 {"message": str(InvalidSku)}
    """
    try:
        cmd = commands.Allocate(**body.dict())
        results = bus.handle(cmd)
        batch_ref = results.pop(0)
    except (handlers.InvalidSku) as error:
        return JSONResponse({"message": str(error)}, status_code=400)

    return JSONResponse({"batchref": batch_ref}, status_code=202)


@app.get("/allocations/{order_id}")
def allocations_view_endpoint(order_id: str):
    try:
        result = views.allocations(order_id, bus.uow)
    except Exception as e:
        logger.info(e);
        raise e

    if not result:
        return JSONResponse({"message": "not found"}, status_code=404)
    return JSONResponse(result, status_code=200)
