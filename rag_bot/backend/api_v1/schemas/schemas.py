from pydantic import BaseModel
from typing import Optional

class FileSchema(BaseModel):
    filename: str
    size: Optional[int] = None
    qdrant_file_id: str