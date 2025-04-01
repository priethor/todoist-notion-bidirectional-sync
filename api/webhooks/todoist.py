"""Handlers for Todoist webhook events."""
import os
import hmac
import hashlib
import json
import logging
import base64
from typing import Dict, Any, Optional, Tuple

from flask import Blueprint, request, jsonify

from api.notion.client import notion_client

logger = logging.getLogger(__name__)

# Get the Todoist client secret from environment variables
TODOIST_CLIENT_SECRET = os.getenv("TODOIST_CLIENT_SECRET")

# Create Blueprint for Todoist webhook routes
todoist_webhook = Blueprint("todoist_webhook", __name__)


def verify_todoist_signature(request_data: bytes, signature: str) -> bool:
    """
    Verify that the webhook request is coming from Todoist.
    
    Args:
        request_data: The raw request body data
        signature: The signature from the X-Todoist-Hmac-SHA256 header
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not TODOIST_CLIENT_SECRET:
        logger.warning("TODOIST_CLIENT_SECRET not set, skipping signature verification")
        return True
    
    # Log key information for debugging
    logger.info(f"Verifying signature: {signature}")
    logger.info(f"Request data length: {len(request_data)} bytes")
    logger.debug(f"Request data: {request_data.decode('utf-8', errors='replace')}")
    
    # Compute digest in base64 format (what Todoist sends)
    computed_hmac_bytes = hmac.new(
        key=TODOIST_CLIENT_SECRET.encode("utf-8"),
        msg=request_data,
        digestmod=hashlib.sha256,
    ).digest()
    
    computed_hmac_base64 = base64.b64encode(computed_hmac_bytes).decode("utf-8")
    
    logger.info(f"Computed HMAC: {computed_hmac_base64}")
    
    is_valid = hmac.compare_digest(computed_hmac_base64, signature)
    if not is_valid:
        logger.warning(f"Signature verification failed. Expected: {computed_hmac_base64}, Got: {signature}")
    
    return is_valid


def process_todoist_event(event_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Process the Todoist webhook event.
    
    Args:
        event_data: The parsed JSON data from the webhook
        
    Returns:
        Tuple[bool, Optional[str]]: Success status and error message if any
    """
    event_type = event_data.get("event_name")
    
    logger.info(f"Processing Todoist event: {event_type}")
    logger.debug(f"Event data: {json.dumps(event_data)}")
    
    try:
        if not event_type:
            return False, "Missing event_name in webhook data"
            
        # Extract task data
        item_data = event_data.get("event_data", {})
        if not item_data:
            return False, "Missing event_data in webhook data"
            
        # Handle different event types
        if event_type == "item:added":
            return handle_item_added(item_data)
        elif event_type == "item:updated":
            return handle_item_updated(item_data)
        elif event_type == "item:completed":
            return handle_item_completed(item_data)
        elif event_type == "item:uncompleted":
            return handle_item_uncompleted(item_data)
        elif event_type == "item:deleted":
            return handle_item_deleted(item_data)
        else:
            logger.info(f"Ignoring unhandled event type: {event_type}")
            return True, None
            
    except Exception as e:
        logger.exception(f"Error processing Todoist event: {str(e)}")
        return False, f"Error processing event: {str(e)}"


def handle_item_added(item_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Handle the item:added event by creating a task in Notion."""
    task_id = item_data.get("id")
    content = item_data.get("content")
    logger.info(f"Handling item:added for task '{content}' (ID: {task_id})")
    
    if not notion_client.is_ready():
        logger.warning("Notion client not ready. Skipping task creation")
        return True, "Notion client not ready"
    
    # Create the task in Notion
    notion_page_id = notion_client.create_task(item_data)
    
    if notion_page_id:
        logger.info(f"Successfully created task in Notion with ID: {notion_page_id}")
        # The Todoist ID is already stored in the Notion page properties
        return True, None
    else:
        logger.warning(f"Failed to create task in Notion: {content}")
        return False, "Failed to create task in Notion"


def handle_item_updated(item_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Handle the item:updated event by updating a task in Notion."""
    task_id = item_data.get("id")
    content = item_data.get("content")
    logger.info(f"Handling item:updated for task '{content}' (ID: {task_id})")
    
    if not notion_client.is_ready():
        logger.warning("Notion client not ready. Skipping task update")
        return True, "Notion client not ready"
    
    # Update the task in Notion
    success = notion_client.update_task(item_data)
    
    if success:
        logger.info(f"Successfully updated task in Notion: {content}")
        return True, None
    else:
        logger.warning(f"Failed to update task in Notion: {content}")
        return False, "Failed to update task in Notion"


def handle_item_completed(item_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Handle the item:completed event by marking a task as completed in Notion."""
    task_id = item_data.get("id")
    content = item_data.get("content")
    logger.info(f"Handling item:completed for task '{content}' (ID: {task_id})")
    
    if not notion_client.is_ready():
        logger.warning("Notion client not ready. Skipping task completion")
        return True, "Notion client not ready"
    
    # Mark the task as completed in Notion
    success = notion_client.complete_task(item_data)
    
    if success:
        logger.info(f"Successfully marked task as completed in Notion: {content}")
        return True, None
    else:
        logger.warning(f"Failed to mark task as completed in Notion: {content}")
        return False, "Failed to mark task as completed in Notion"


def handle_item_uncompleted(item_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Handle the item:uncompleted event by marking a task as not completed in Notion."""
    task_id = item_data.get("id")
    content = item_data.get("content")
    logger.info(f"Handling item:uncompleted for task '{content}' (ID: {task_id})")
    
    if not notion_client.is_ready():
        logger.warning("Notion client not ready. Skipping task un-completion")
        return True, "Notion client not ready"
    
    # Mark the task as not completed in Notion
    success = notion_client.uncomplete_task(item_data)
    
    if success:
        logger.info(f"Successfully marked task as not completed in Notion: {content}")
        return True, None
    else:
        logger.warning(f"Failed to mark task as not completed in Notion: {content}")
        return False, "Failed to mark task as not completed in Notion"


def handle_item_deleted(item_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Handle the item:deleted event by deleting or archiving a task in Notion."""
    task_id = item_data.get("id")
    content = item_data.get("content", "Unknown")
    logger.info(f"Handling item:deleted for task '{content}' (ID: {task_id})")
    
    if not notion_client.is_ready():
        logger.warning("Notion client not ready. Skipping task deletion")
        return True, "Notion client not ready"
    
    # Delete the task in Notion
    success = notion_client.delete_task(item_data)
    
    if success:
        logger.info(f"Successfully deleted task in Notion: {content}")
        return True, None
    else:
        logger.warning(f"Failed to delete task in Notion: {content}")
        return False, "Failed to delete task in Notion"


@todoist_webhook.route("/todoist", methods=["GET", "POST"])
def handle_webhook():
    """Handle incoming webhook events from Todoist."""
    # Handle initial webhook verification (GET request)
    if request.method == "GET":
        logger.info("Received webhook verification request")
        verification_token = request.args.get("verification_token")
        
        if not verification_token:
            logger.warning("No verification token provided")
            return jsonify({"status": "error", "message": "No verification token provided"}), 400
            
        logger.info(f"Responding with verification token: {verification_token}")
        return verification_token, 200
    
    # Handle actual webhook events (POST requests)
    # Get raw request data for signature verification
    request_data = request.get_data()
    
    # Get the signature from the headers
    signature = request.headers.get("X-Todoist-Hmac-SHA256", "")
    
    # Verify signature
    if not verify_todoist_signature(request_data, signature):
        logger.warning("Invalid Todoist webhook signature")
        return jsonify({"status": "error", "message": "Invalid signature"}), 401
    
    # Parse the JSON data
    try:
        event_data = request.json
        logger.info(f"Received Todoist webhook: {event_data.get('event_name', 'unknown_event')}")
    except Exception as e:
        logger.error(f"Error parsing webhook data: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid JSON data"}), 400
    
    # Process the event
    success, error_message = process_todoist_event(event_data)
    
    if not success:
        return jsonify({"status": "error", "message": error_message}), 500
    
    return jsonify({"status": "success"}), 200