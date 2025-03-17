import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define configuration settings
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", )
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "https://sqs.ap-south-1.amazonaws.com/428590250375/Testing.fifo")
EVENT_NETTING_SERVICE_URL = os.environ.get("EVENT_NETTING_SERVICE_URL")
EVENT_NETTING_REQUIRED = os.environ.get("EVENT_NETTING_REQUIRED", "False").lower() == "true"  # Default to False if not set

# Check for required variables
required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "SQS_QUEUE_URL"]
for var in required_vars:
    if not os.environ.get(var):
        raise ValueError(f"Missing required environment variable: {var}")


if __name__ == '__main__':
    # Example usage and testing
    print(f"AWS Access Key ID: {AWS_ACCESS_KEY_ID}")
    print(f"SQS Queue URL: {SQS_QUEUE_URL}")
    print(f"Event Netting Service URL: {EVENT_NETTING_SERVICE_URL}")
    print(f"Event Netting Required: {EVENT_NETTING_REQUIRED}")