from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class NoteBase(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    created_at: datetime
    summary: Optional[str] = None
    
    class Config:
        from_attributes = True
