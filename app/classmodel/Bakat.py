from pydantic import BaseModel
from typing import List

class JSONBakatRequest(BaseModel):
    bakat_id: List[int]