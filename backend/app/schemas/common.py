from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    data: List[T]
    total: int
