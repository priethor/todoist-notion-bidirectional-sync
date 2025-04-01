"""Webhook handlers for external services."""
from flask import Blueprint

from api.webhooks.todoist import todoist_webhook

# Create main webhooks blueprint
webhooks = Blueprint("webhooks", __name__, url_prefix="/webhook")

# Register Todoist webhooks
webhooks.register_blueprint(todoist_webhook)
