from contextlib import suppress
from typing import Any

from app.constants.commom import CommonConst


class CommonUtils:
    @classmethod
    def safe_int(cls, value: Any) -> int:
        """Convert an any to an integer"""
        with suppress(ValueError):
            return int(value)
        return CommonConst.ZERO

    @classmethod
    def safe_bool(cls, value: Any) -> bool:
        """Convert an any to a boolean"""
        with suppress(ValueError):
            return bool(value)
        return False
