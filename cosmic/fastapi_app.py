# pylint: disable=too-few-public-methods
"fastapi app"

# pylint: disable=no-name-in-module
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI,Body
from starlette.responses import JSONResponse

# import config
import model
import orm
import repository
import services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine("sqlite:///test.db"))
# config.get_postgres_uri()))
app = FastAPI()


class OrderLineDto(BaseModel):
    "OrderLine의 Pydantic 모델. 귀찮군..."
    orderid: str
    sku: str
    quantity: int

def get_session_and_repo():
    "session과 repo를 생성"
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    return session, repo

@app.post("/allocate")
def allocate_endpoint(body: OrderLineDto = Body(default=None)):
    """
    req
    - body : OrderLineDto

    res
    - 201 {"batchref": str}
    - 400 {"message": str(OutOfStock or InvalidSku)}
    """
    line = model.OrderLine(**body.dict())

    session, repo = get_session_and_repo()

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as error:
        return JSONResponse({"message": str(error)}, 400)

    return JSONResponse({"batchref": batchref}, status_code=201)
