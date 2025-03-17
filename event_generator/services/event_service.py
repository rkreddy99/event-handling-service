import boto3
import json
import requests
from ..config import AWS_REGION, SQS_QUEUE_URL, EVENT_NETTING_SERVICE_URL, EVENT_NETTING_REQUIRED
from ..models import BaseEvent
import hashlib

class EventService:
    """
    Handles event processing: sending to SQS and event netting (if required).
    """

    def __init__(self):
        self.sqs_client = boto3.client(
            "sqs", AWS_REGION
        )

    def send_to_sqs(self, event_data: BaseEvent):
        """
        Sends an event to the SQS queue.
        """
        try:
            # Create a JSON-serializable version of the event data
            event_json = event_data.model_dump()
            event_json["timestamp"] = event_json["timestamp"].isoformat()
            
            message_body = json.dumps(event_json)
            
            response = self.sqs_client.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=message_body,
                MessageGroupId=event_data.event_type,
                MessageDeduplicationId=hashlib.md5(json.dumps(event_json, sort_keys=True).encode('utf-8')).hexdigest()
            )
            print(f"Sent event to SQS: {response['MessageId']}")
            return True
        except Exception as e:
            print(f"Error sending to SQS: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def send_to_event_netting(self, event: BaseEvent):
        """
        Sends an event to the event netting service.
        """
        if not EVENT_NETTING_SERVICE_URL:
            print("Event netting service URL not configured.")
            return False
        try:
            response = requests.post(EVENT_NETTING_SERVICE_URL, json=event.model_dump())
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            print(f"Sent event to event netting service. Status code: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending to event netting service: {e}")
            return False

    def process_event(self, event: BaseEvent):
        """
        Processes an event: sends it to SQS and optionally to the event netting service.
        """
        print(f"Processing event: {event.event_type}")
        sqs_success = self.send_to_sqs(event)

        if EVENT_NETTING_REQUIRED:
            netting_success = self.send_to_event_netting(event)
            return sqs_success and netting_success # Return True if both operations were successful
        return sqs_success  # Return True if SQS send was successful (netting is not required)

# Example usage (for testing)
if __name__ == '__main__':
    # Replace with your actual event data
    example_event = {
        "event_type": "example_event",
        "data": {"message": "This is a test event."}
    }
    service = EventService()
    service.process_event(example_event)