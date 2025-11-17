from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SearchResult(BaseModel):
    """Model for web search results"""
    title: str
    snippet: str
    url: Optional[str] = None


class ResearchNote(BaseModel):
    """Model for research notes"""
    topic: str = Field(description="The research topic")
    content: str = Field(description="The research findings and notes")
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: List[str] = Field(default_factory=list)