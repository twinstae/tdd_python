"""table -> model 맵핑"""

from sqlalchemy.orm import mapper, relationship

import db_tables
from domain import model


def start_mappers():
    """db_tables를 model에 mapping 한다."""

    lines_mapper = mapper(model.OrderLine, db_tables.order_lines)
    mapper(
        model.Batch,
        db_tables.batches,
        properties={
            "_allocations": relationship(
                lines_mapper, secondary=db_tables.allocations, collection_class=set,
            )
        },
    )
