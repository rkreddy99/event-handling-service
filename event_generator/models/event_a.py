from pydantic import Field
from .base_event import BaseEvent

class EventA(BaseEvent):
    """
    Specific event type A.
    """
    strategy: str = Field(..., description="Strategy is required")
    date: str = Field(..., description="Date is required")