# Todoist-Notion Bidirectional Sync

A Python application that provides bidirectional synchronization between Todoist tasks and Notion database entries.

## Features

- Receive webhooks from Todoist when tasks are created, updated, completed, or deleted
- Process task changes and sync them to Notion (placeholder implementation)
- Store Todoist IDs directly in Notion for seamless integration
- (Coming soon) Full Notion database integration with two-way sync
- (Coming soon) Sync entries from Notion to Todoist
- (Coming soon) Bidirectional conflict resolution

## Setup

### Prerequisites

- Python 3.9+
- Todoist account with API access
- Notion account with API access
- A publicly accessible endpoint for receiving webhooks (e.g., ngrok for local development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/todoist-notion-bidirectional-sync.git
   cd todoist-notion-bidirectional-sync
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template and update with your API keys:
   ```bash
   cp .env.template .env
   # Edit .env with your Todoist and Notion API credentials
   ```

### Todoist Webhook Setup

1. Set up a publicly accessible endpoint to receive webhooks (e.g., using ngrok):
   ```bash
   ngrok http 5001
   ```

2. Create a webhook in Todoist using the [Todoist Developer console](https://developer.todoist.com/appconsole.html):
   - URL: `https://your-ngrok-url.ngrok.io/webhook/todoist`
   - Events: Select the events you want to receive (item:added, item:updated, item:completed, etc.)
   - Service: Create a new service and note the Client Secret
   - Add the Client Secret to your `.env` file as `TODOIST_CLIENT_SECRET`

## Running the Application

Start the Flask server:
```bash
python3 app.py
```

## Testing

You can test the webhook endpoint using the provided test script:

```bash
python3 scripts/test_webhook.py --event item:added --payload scripts/sample_payloads/item_added.json
```

This will send a simulated webhook to `http://localhost:5001/webhook/todoist` by default. You can specify a different URL with the `--url` parameter.

## Project Structure

```
├── api/
│   ├── __init__.py
│   ├── notion/
│   │   ├── __init__.py
│   │   └── client.py        # Notion API client for task synchronization
│   └── webhooks/
│       ├── __init__.py      # Registers all webhook blueprints
│       └── todoist.py       # Todoist webhook handler and routes
├── docs/
│   └── DESIGN.md            # Design document with PARA method integration details
├── scripts/
│   ├── sample_payloads/     # Example webhook payloads
│   └── test_webhook.py      # Script to test webhook locally
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
└── .env.template            # Environment variables template
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.