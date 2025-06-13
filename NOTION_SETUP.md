# Notion Setup Guide

Set up your Notion workspace to sync with Todoist.

## 1. Create Notion Integration

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create new integration named "Todoist Sync"
3. Enable read/write permissions
4. Copy the **Internal Integration Token** for your `.env` file

## 2. Create Databases

### Areas Database
**Required properties:**
- **Name** (Title) - project name from Todoist
- **Todoist Project ID** (Text) - for mapping projects
- **Tasks** (Relation → Tasks database) - linked tasks

**Optional properties:**
- **Description** (Text) - project details
- **Deleted** (Checkbox) - for soft deletion

### Tasks Database  
**Required properties:**
- **Name** (Title) - task content from Todoist
- **Todoist ID** (Text) - for mapping tasks
- **Status** (Select: "Not Started", "Completed") - completion status
- **Area** (Relation → Areas database) - project relationship

**Optional properties:**
- **Due Date** (Date) - task due date
- **Priority** (Select: "Normal", "Low", "Medium", "High") - priority level
- **Description** (Text) - task notes
- **Labels** (Multi-select) - Todoist labels as tags
- **Deleted** (Checkbox) - for soft deletion

## 3. Share Databases

Share both databases with your "Todoist Sync" integration and give edit permissions.

## 4. Get Database IDs

Copy the 32-character database ID from each database's share URL:
```
https://notion.so/workspace/DatabaseName-abc123def456...
                                         ^database ID^
```

## 5. Environment Configuration

Create `.env` file:
```env
NOTION_API_KEY=your_integration_token
NOTION_TASK_DATABASE_ID=your_tasks_database_id  
NOTION_AREAS_DATABASE_ID=your_areas_database_id
TODOIST_CLIENT_SECRET=from_todoist_webhook_setup
```

## 6. Validate Setup

Test your configuration before running the full sync:

```bash
# Validate complete setup (Todoist + Notion)
python3 -m api.setup_validator

# Or validate just Notion
python3 -m api.notion.validator

# Or from Python
from api.setup_validator import SetupValidator
validator = SetupValidator()
validator.print_validation_report()
```

This will check:
- ✅ Todoist client secret configuration
- ✅ Notion SDK installation
- ✅ Environment variables
- ✅ API key authentication  
- ✅ Database access permissions
- ✅ Required database properties

## 7. Test Full Integration

1. Start the app: `python3 app.py`
2. Configure Todoist webhook (see WEBHOOK_SETUP.md)
3. Create a task in Todoist
4. Verify it appears in your Notion Tasks database

Your sync is ready!