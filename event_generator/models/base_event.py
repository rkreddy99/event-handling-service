from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime

class BaseEvent(BaseModel):
    """
    Base class for all events. Provides common fields and validation.
    """

    model_config = ConfigDict(extra="allow")

    event_type: str = Field(..., description="Event type is required")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the event (auto-generated if not provided)")
    source: Optional[str] = Field(None, description="Origin of the event (optional)") # Added optional source field

    @field_validator('event_type')
    def event_type_must_not_be_empty(cls, value):
        if not value:
            raise ValueError('Event type cannot be empty')
        return value
