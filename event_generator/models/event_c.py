from pydantic import Field
from .base_event import BaseEvent

class EventC(BaseEvent):
    """
    Specific event type C.
    """
    strategy: str = Field(..., description="Strategy is required")
    hash: str = Field(..., description="Hash is required")