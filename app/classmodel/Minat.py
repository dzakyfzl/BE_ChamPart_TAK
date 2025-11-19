from pydantic import BaseModel
from typing import List

class JSONMinatRequest(BaseModel):
    minat_id: List[int]
