# Todoist Webhook Setup Guide

Follow these steps to set up and test your Todoist webhook integration locally.

## 1. Configure ngrok

You need ngrok to expose your local server to the internet so Todoist can send webhooks to it.

```bash
# Configure ngrok with your authtoken (only needed once)
ngrok config add-authtoken YOUR_AUTHTOKEN_FROM_DASHBOARD
```

## 2. Start ngrok to create a tunnel

```bash
# Run this in a terminal window (keep it open)
cd /Users/priethor/Documents/GitHub/todoist-notion-bidirectional-sync
ngrok http 5001
```

This will display a URL like `https://abc123.ngrok.io` - copy this URL.

## 3. Create a Todoist Integration

1. Go to [Todoist Developer Console](https://developer.todoist.com/appconsole.html)
2. Click "Create new app"
3. Fill in the required information:
   - Name: "Todoist-Notion Sync"
   - Description: "Syncs tasks between Todoist and Notion"
   - OAuth Redirect URI: (can be left empty for this use case)

4. After creating the app, navigate to the "Webhooks" section
5. Click "Add webhook"
6. Configure the webhook:
   - Service URL: Your ngrok URL + `/webhook/todoist` (e.g., `https://abc123.ngrok.io/webhook/todoist`)
   - Events: Select events you want to receive (e.g., `item:added`, `item:updated`, `item:completed`)

7. Save the webhook and note the following:
   - Verification process: Todoist will send a GET request to verify your endpoint
   - Client Secret: Copy this value for your .env file

**Important:** The initial verification is automatic. Our application will echo back the verification token that Todoist sends.

## 4. Configure your .env file

Edit your `.env` file to add the Todoist client secret:

```
# Todoist API
TODOIST_API_TOKEN=your_todoist_api_token
TODOIST_CLIENT_SECRET=the_client_secret_you_copied
```

## 5. Start your Flask application

```bash
# Run this in a new terminal window (keep it open)
cd /Users/priethor/Documents/GitHub/todoist-notion-bidirectional-sync
python3 app.py
```

## 6. Test the webhook

1. Go to your Todoist account
2. Create a new task
3. Check your Flask application's logs to see the webhook event

You should see log messages indicating that your application received the webhook and processed the event.

## Troubleshooting

- If webhooks aren't being received, check that ngrok is running and the URL in the Todoist webhook configuration is correct
- Check that the client secret in your `.env` file matches the one from Todoist
- Verify that your Flask application is running and listening on port 5000
- Look for any errors in the Flask application logs