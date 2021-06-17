from sqlalchemy.orm import mapper, relationship

import db_tables
import model

def start_mappers():
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
