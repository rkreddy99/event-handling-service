import json
from db import Database
from api_client import ApiClient
from sqs_service import SQSService

def main(event):
    db = Database()
    db.init()
    try:
        for record in event['Records']:
            queue_url = get_queue_url(record['eventSourceARN'])
            user = db.fetch_user_by_queue_url(queue_url)

            if user:
                ip_port = user["ip_port"]
                token = user["token"]
                print(f"Fetched user details: {user}")

                # Example payload for the POST request
                payload = record['body']
                payload['username'] = user['username']
                payload = json.dumps(payload)
                api_client = ApiClient()
                response = api_client.post_request(ip_port, token, payload)

                if response:
                    print("POST Response:", response)
                    # delete record from queue
                    delete_record_from_queue(record, queue_url)
                else:
                    print("Failed to get a response.")
            else:
                print(f"No user found with queue_url: {queue_url}")
    finally:
        db.close()

def delete_record_from_queue(record, queue_url=None):
    """ deletes event from queue """
    # delete event from queue
    region_name = "us-east-1"
    receipt_handle = record['receiptHandle'] 
    if queue_url == None:      
        queue_url = get_queue_url(record['eventSourceARN'])
    
    sqs_service = SQSService(queue_url=queue_url, region_name=region_name)
    # Delete the message
    try:
        sqs_service.delete_message(receipt_handle)
    except Exception as e:
        print(f"Error deleting message: {str(e)}")


def get_queue_url(queue_arn):
    """ returns queue url """
    # Extract queue ARN
    region = queue_arn.split(":")[3]
    account_id = queue_arn.split(":")[4]
    queue_name = queue_arn.split(":")[5]

    # Construct queue URL
    queue_url = f"https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}"

    print(f"Queue URL: {queue_url}")
    return queue_url

if __name__ == "__main__":
    main()

