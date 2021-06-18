# pylint: disable=too-few-public-methods
"fastapi app"

# pylint: disable=no-name-in-module
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI,Body
from starlette.responses import JSONResponse

# import config
from domain import model
from adapters import orm
from adapters import repository
from service_layer import services


# config.get_postgres_uri()))
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    orm.start_mappers()
    app.state.get_session = sessionmaker(bind=create_engine("sqlite:///test.db"))

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


def get_session_and_repo():
    """session과 repo를 생성"""
    session = app.state.get_session()
    repo = repository.SqlAlchemyRepository(session)
    return session, repo


@app.post("/add_batch")
def add_batch(body: BatchDto = Body(None)):
    session, repo = get_session_and_repo()

    eta = body.eta
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    services.add_batch(
        body.ref,
        body.sku,
        body.quantity,
        eta,
        repo=repo,
        session=session,
    )
    return JSONResponse({"ok": True}, status_code=201)


@app.post("/allocate")
def allocate_endpoint(body: OrderLineDto = Body(default=None)):
    """
    req
    - body : OrderLineDto

    res
    - 201 {"batchref": str}
    - 400 {"message": str(OutOfStock or InvalidSku)}
    """
    session, repo = get_session_and_repo()

    try:
        batchref = services.allocate(**body.dict(), repo=repo, session=session)
    except (model.OutOfStock, services.InvalidSku) as error:
        return JSONResponse({"message": str(error)}, status_code=400)

    return JSONResponse({"batchref": batchref}, status_code=201)
