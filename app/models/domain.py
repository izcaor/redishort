from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ContentItem(BaseModel):
    source_id: str = Field(..., description="Unique ID from source")
    source_type: str = Field(..., description="Type of source (e.g., reddit, rss, url)")
    title: str = Field(..., description="Content title")
    content_text: str = Field(..., description="Main text body")
    author: Optional[str] = Field(None, description="Original author")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @property
    def display_title(self) -> str:
        return self.title[:60] + "..." if len(self.title) > 60 else self.title
