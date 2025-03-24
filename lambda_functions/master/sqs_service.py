import boto3
import json
import hashlib
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

class SQSService:
    def __init__(self, queue_url: str, region_name: str = 'us-east-1'):
        """
        Initialize the SQS service.
        
        Args:
            queue_url (str): The URL of the SQS queue
            region_name (str): AWS region name (default: 'us-east-1')
        """
        if not queue_url.endswith('.fifo'):
            raise ValueError("Queue URL must end with .fifo for FIFO queues")
            
        self.queue_url = queue_url
        self.sqs = boto3.client('sqs', region_name=region_name)

    def send_message(self, 
                     message_body: Dict[str, Any], 
                     message_group_id: str,
                     deduplication_id: Optional[str] = None,
                     delay_seconds: int = 0) -> Optional[str]:
        """
        Send a message to the FIFO SQS queue.
        
        Args:
            message_body (dict): The message to send
            message_group_id (str): Message group ID (required for FIFO)
            deduplication_id (str, optional): Custom deduplication ID
            delay_seconds (int): Delay delivery of the message
            
        Returns:
            Optional[str]: MessageId if successful, None if failed
        """
        try:
            # Prepare message parameters
            message_params = {
                'QueueUrl': self.queue_url,
                'MessageBody': json.dumps(message_body),
                'MessageGroupId': message_group_id,
                'DelaySeconds': delay_seconds
            }
            
            # Add deduplication ID (required unless content-based deduplication is enabled)
            if deduplication_id:
                message_params['MessageDeduplicationId'] = deduplication_id
            else:
                # Generate a UUID if no deduplication ID is provided
                # Create MD5 hash of the message body for deduplication
                message_hash = hashlib.md5(json.dumps(message_body, sort_keys=True).encode('utf-8')).hexdigest()
                message_params['MessageDeduplicationId'] = message_hash

            response = self.sqs.send_message(**message_params)
            message_id = response.get('MessageId')
            print(f"Message sent successfully. MessageId: {message_id}")
            return message_id
            
        except ClientError as e:
            print(f"Failed to send message: {str(e)}")
            return None

    def receive_messages(self, max_messages: int = 1, wait_time_seconds: int = 20) -> list:
        """
        Receive messages from the FIFO queue.
        
        Args:
            max_messages (int): Maximum number of messages to receive (1-10)
            wait_time_seconds (int): Long polling wait time
            
        Returns:
            list: List of received messages
        """
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            messages = response.get('Messages', [])
            print(f"Received {len(messages)} messages")
            return messages
        except ClientError as e:
            print(f"Failed to receive messages: {str(e)}")
            return []

    def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a message from the queue after processing.
        
        Args:
            receipt_handle (str): The receipt handle of the message to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            print("Message deleted successfully")
            return True
        except ClientError as e:
            print(f"Failed to delete message: {str(e)}")
            return False

