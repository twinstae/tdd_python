"""테스트용 helper, util 함수"""

import random
import uuid

COLORS = [
    "RED", "BLUE", "GREEN", "YELLOW", "PINK",
    "WHITE", "BLACK", "BROWN", "GRAY", "PURPLE"
]

FURNITURE_TYPES = [
    "SOFA", "COFFEE-TABLE", "CHAIR", "LAMP", "BED", "CUSHION",
    "ARM-CHAIR", "SIDE-TABLE", "RUG", "WALL-DECOR", "CLOCK"
]


def random_suffix():
    "uuid로 무작위 6개 hex를 생성"
    return uuid.uuid4().hex[:6]


def random_sku(furniture_type="") -> str:
    """
    무작위로 생성한 SKU를 반환.
    color 목록과 furniture_type 목록에서 무작위로 한 개씩 골라서 조합하고, UUID를 덧붙입니다.
    (총 10 x 11 = 110가지 조합. ex \"BLUE-SOFA\" \"PINK-BED\")
    """

    color = random.choice(COLORS)
    if furniture_type == "":
        furniture_type = random.choice(FURNITURE_TYPES)
    return f"{color}-{furniture_type}-{random_suffix()}"


def random_batchref(name="") -> str:
    "batch-{name}-{random_suffix()}"
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name="") -> str:
    "order-{name}-{random_suffix()}"
    return f"order-{name}-{random_suffix()}"
