from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    request_id: Optional[str] = None


class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    meta: Meta = Meta()
    error: Optional[dict] = None
