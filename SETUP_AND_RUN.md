# Setup and Run Guide

Follow these steps to set up and run the Todoist-Notion sync application using a virtual environment.

## 1. Navigate to the project directory

```bash
cd /Users/priethor/Documents/GitHub/todoist-notion-bidirectional-sync
```

## 2. Activate the virtual environment

On macOS/Linux:
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt indicating the virtual environment is active.

## 3. Install the required dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure your environment variables

Copy the template and edit the `.env` file:
```bash
cp .env.template .env
# Edit .env to add your API keys and credentials
```

## 5. Run the application

```bash
python app.py
```

The application will start, and you should see output like:
```
* Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
```

## 6. Expose your local server using ngrok (in a separate terminal)

In a new terminal window:
```bash
cd /Users/priethor/Documents/GitHub/todoist-notion-bidirectional-sync
ngrok http 5001
```

This will give you a public URL that you can use to configure your Todoist webhook.

## 7. Deactivate the virtual environment when done

When you're finished, you can deactivate the virtual environment:
```bash
deactivate
```

See `WEBHOOK_SETUP.md` for detailed instructions on setting up the Todoist webhook integration.