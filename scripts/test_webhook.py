"""Script to simulate a Todoist webhook event for testing."""
import argparse
import json
import os
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

TODOIST_CLIENT_SECRET = os.getenv("TODOIST_CLIENT_SECRET")


def generate_signature(data: str) -> str:
    """Generate Todoist webhook signature."""
    if not TODOIST_CLIENT_SECRET:
        raise ValueError("TODOIST_CLIENT_SECRET not set")
        
    return hmac.new(
        key=TODOIST_CLIENT_SECRET.encode("utf-8"),
        msg=data.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def simulate_webhook(webhook_url: str, event_name: str, payload_file: str = None) -> None:
    """Simulate a Todoist webhook request."""
    # Use sample payload or load from file
    if payload_file:
        with open(payload_file, "r") as f:
            payload = json.load(f)
    else:
        # Sample payload for item:added event
        payload = {
            "event_name": event_name,
            "user_id": 12345678,
            "event_data": {
                "id": "2995104339",
                "checked": False,
                "content": "Test task",
                "description": "",
                "due": None,
                "priority": 1,
                "project_id": "2203306141",
                "section_id": None,
                "parent_id": None,
                "user_id": 12345678,
                "added_by_uid": 12345678
            },
            "version": "9"
        }
    
    # Add event_name if not included
    if "event_name" not in payload:
        payload["event_name"] = event_name
    
    # Convert payload to JSON string
    payload_json = json.dumps(payload)
    
    # Generate signature
    signature = generate_signature(payload_json)
    
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "X-Todoist-Hmac-SHA256": signature,
    }
    
    # Send request
    response = requests.post(webhook_url, data=payload_json, headers=headers)
    
    # Print response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a Todoist webhook request")
    parser.add_argument(
        "--url", 
        type=str, 
        default="http://localhost:5001/webhook/todoist",
        help="Webhook URL to send the request to (default: http://localhost:5001/webhook/todoist)"
    )
    parser.add_argument(
        "--event", 
        type=str, 
        default="item:added", 
        help="Event name (e.g., item:added, item:updated, item:deleted)"
    )
    parser.add_argument(
        "--payload", 
        type=str, 
        help="Path to JSON file containing the payload"
    )
    
    args = parser.parse_args()
    
    simulate_webhook(args.url, args.event, args.payload)