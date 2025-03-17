from pydantic import Field
from .base_event import BaseEvent

class EventB(BaseEvent):
    """
    Specific event type B.
    """
    strategy: str = Field(..., description="Strategy is required")
    date: str = Field(..., description="Date is required")
    exchange: str = Field(..., description="Exchange is required")