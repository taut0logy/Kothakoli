from typing import List, TypeVar, Generic
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int 