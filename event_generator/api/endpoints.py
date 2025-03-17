from fastapi import FastAPI, HTTPException
from fastapi import Depends
from ..models import *
from ..services.event_service import EventService

app = FastAPI()

# Define a mapping of event types to their corresponding Pydantic models
# EVENT_TYPE_MAPPING = {
#     "event_a": EventA,
#     "event_b": EventB,
#     "event_c": EventC,
# }

async def get_event_service() -> EventService:
    return EventService()

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "OK"}


@app.post("/events/")
async def create_event(event: BaseEvent, event_service: EventService = Depends(get_event_service)):
    """
    Endpoint to receive events.
    """
    # event_type = event.event_type
    # event_model = EVENT_TYPE_MAPPING.get(event_type)

    # if event_model:
    print("Event input", event)

    # if event_service.process_event(event):
    #     return {"message": "Event received and processed"}
    # else:
    #     raise HTTPException(status_code=500, detail="Event processing failed")
    try:
        event_service.process_event(event)
        return {"message": "Event received and processed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))