import typer
import json
from pathlib import Path
from services.event_service import EventService
from models.base_event import BaseEvent
from models.event_a import EventA
from models.event_b import EventB
from models.event_c import EventC
from typing_extensions import Annotated

app = typer.Typer()

@app.command()
def submit_event(
    event_file: Annotated[Path, typer.Option(help="Path to the JSON event file")],
):
    """
    Submit an event from a JSON file.
    """
    try:
        with open(event_file, "r") as f:
            event_data = json.load(f)
            event = BaseEvent(**event_data)

            # if event.event_type == "event_a":
            #     event = EventA(**event.model_dump())
            # elif event.event_type == "event_b":
            #     event = EventB(**event.model_dump())
            # elif event.event_type == "event_c":
            #     event = EventC(**event.model_dump())
            # else:
            #      pass # if other event just pass to SQS


            event_service = EventService()
            if event_service.process_event(event.model_dump()):
                typer.echo("Event submitted successfully.")
            else:
                typer.echo("Event submission failed.", err=True)

    except FileNotFoundError:
        typer.echo(f"Error: File not found: {event_file}", err=True)
    except json.JSONDecodeError:
        typer.echo(f"Error: Invalid JSON in file: {event_file}", err=True)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)

@app.command()
def health_check():
    """
    Check the health of the event processing service.
    """
    typer.echo("Health check: OK")  # Placeholder - Implement actual health check logic if needed.

if __name__ == "__main__":
    app()