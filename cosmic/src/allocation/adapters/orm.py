"""table -> model 맵핑"""

from sqlalchemy import MetaData
from sqlalchemy.orm import mapper, relationship
from sqlalchemy.exc import ArgumentError
from sqlalchemy.sql.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import Integer, String, Date

from allocation.domain import model

metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("quantity", Integer, nullable=False), # 수량
    Column("orderid", String(255)),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ref", String(255)),
    Column("sku", ForeignKey("products.sku")),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)

products = Table(
    "products",
    metadata,
    Column("sku", String(255), primary_key=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)

def start_mappers():
    """db table을 model에 mapping 한다."""

    try:
        lines_mapper = mapper(model.OrderLine, order_lines)
        batches_mapper = mapper(
            model.Batch,
            batches,
            properties={
                "_allocations": relationship(
                    lines_mapper,
                    secondary=allocations,
                    collection_class=set,
                )
            },
        )

        mapper(
            model.Product,
            products,
            properties={ "batches": relationship(batches_mapper) }
        )
    except ArgumentError:
        pass
