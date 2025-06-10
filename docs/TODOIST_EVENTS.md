# Todoist Webhook Events Documentation

This document describes the webhook events that Todoist sends to your application and their payload structure.

## Overview

Todoist sends webhooks for the following task lifecycle events:

- `item:added` - A new task was created
- `item:updated` - An existing task was modified
- `item:completed` - A task was marked as completed
- `item:uncompleted` - A task was marked as incomplete (undone)
- `item:deleted` - A task was permanently deleted

## Event Structure

All webhook events follow this basic structure:

```json
{
  "event_name": "event_type",
  "user_id": 12345678,
  "event_data": {
    // Task data specific to the event
  },
  "version": "9"
}
```

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_name` | string | The type of event (see Event Types below) |
| `user_id` | integer | The ID of the user who triggered the event |
| `event_data` | object | The task data (structure varies by event) |
| `version` | string | Todoist API version |

## Event Types

### 1. `item:added`

Triggered when a new task is created in Todoist.

**Example Payload:**
```json
{
  "event_name": "item:added",
  "user_id": 12345678,
  "event_data": {
    "id": "2995104339",
    "checked": false,
    "content": "New task from Todoist",
    "description": "Task description with details",
    "due": {
      "date": "2025-01-10",
      "is_recurring": false,
      "string": "Jan 10",
      "timezone": "Europe/Madrid"
    },
    "priority": 3,
    "project_id": "2203306141",
    "section_id": null,
    "parent_id": null,
    "user_id": 12345678,
    "labels": ["work", "important"],
    "added_by_uid": 12345678
  },
  "version": "9"
}
```

### 2. `item:updated`

Triggered when an existing task is modified (content, due date, priority, labels, etc.).

**Example Payload:**
```json
{
  "event_name": "item:updated",
  "user_id": 12345678,
  "event_data": {
    "id": "2995104339",
    "checked": false,
    "content": "Updated task from Todoist",
    "description": "Updated task description with more details",
    "due": {
      "date": "2025-01-15",
      "is_recurring": false,
      "string": "Jan 15",
      "timezone": "Europe/Madrid"
    },
    "priority": 4,
    "project_id": "2203306141",
    "section_id": null,
    "parent_id": null,
    "user_id": 12345678,
    "labels": ["work", "important", "urgent"],
    "added_by_uid": 12345678
  },
  "version": "9"
}
```

### 3. `item:completed`

Triggered when a task is marked as completed.

**Example Payload:**
```json
{
  "event_name": "item:completed",
  "user_id": 12345678,
  "event_data": {
    "id": "2995104339",
    "checked": true,
    "content": "Completed task from Todoist",
    "description": "This task is now marked as completed",
    "due": {
      "date": "2025-01-10",
      "is_recurring": false,
      "string": "Jan 10",
      "timezone": "Europe/Madrid"
    },
    "priority": 3,
    "project_id": "2203306141",
    "section_id": null,
    "parent_id": null,
    "user_id": 12345678,
    "labels": ["work", "important"],
    "completed_at": "2025-01-09T15:30:45.000Z",
    "added_by_uid": 12345678
  },
  "version": "9"
}
```

### 4. `item:uncompleted`

Triggered when a previously completed task is marked as incomplete again.

**Payload Structure:** Same as `item:added` but with `checked: false` and no `completed_at` field.

### 5. `item:deleted`

Triggered when a task is permanently deleted from Todoist.

**Payload Structure:** Contains basic task information including `id` and `content`, but may have fewer fields than other events.

## Task Data Fields

### Core Task Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique task identifier |
| `content` | string | ✅ | Task title/name |
| `description` | string | ❌ | Task description/notes |
| `checked` | boolean | ✅ | Completion status (true = completed) |
| `user_id` | integer | ✅ | Owner of the task |
| `added_by_uid` | integer | ✅ | User who originally created the task |

### Organization & Hierarchy

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | string | ✅ | ID of the containing project |
| `section_id` | string/null | ❌ | ID of the section within the project |
| `parent_id` | string/null | ❌ | ID of parent task (for subtasks) |
| `labels` | array[string] | ❌ | List of label names |

### Scheduling & Priority

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `priority` | integer | ✅ | Priority level (1-4, where 4 = highest) |
| `due` | object/null | ❌ | Due date information (see Due Date Object) |

### Completion Tracking

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `completed_at` | string | ❌ | ISO 8601 timestamp when task was completed (only in `item:completed`) |

## Due Date Object

When a task has a due date, the `due` field contains:

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Due date in YYYY-MM-DD format |
| `is_recurring` | boolean | Whether this is a recurring task |
| `string` | string | Human-readable due date (e.g., "Jan 10") |
| `timezone` | string | Timezone for the due date |

## Priority Levels

Todoist uses a 1-4 priority scale:

| Value | Meaning | Color |
|-------|---------|--------|
| 1 | Normal (default) | No color |
| 2 | Low priority | Blue |
| 3 | Medium priority | Orange |
| 4 | High priority | Red |

## Labels

Labels are provided as an array of strings containing the label names (not IDs):

```json
"labels": ["work", "important", "urgent"]
```

## Integration Notes

### For Notion Sync

- Use `id` as the unique identifier to map between Todoist and Notion
- Map `project_id` to Notion Areas in your PARA structure
- Convert `priority` values to your Notion priority system
- Store `labels` as a multi-select property in Notion
- Use `due.date` and `due.timezone` for accurate due date sync

### Event Processing

1. Always check for the `id` field to identify which task the event refers to
2. For `item:updated`, compare timestamps to handle conflicts
3. For `item:deleted`, implement soft deletion in Notion (set Deleted flag)
4. For `item:completed`, update both completion status and timestamp
5. Handle `item:uncompleted` by reversing completion status

## Testing

Use the sample payloads in `scripts/sample_payloads/` to test your webhook handling:

```bash
python3 scripts/test_webhook.py --event item:added --payload scripts/sample_payloads/item_added.json
```

## Security

All webhook requests are signed with HMAC-SHA256. See [TODOIST_SIGNATURE_GUIDE.md](../TODOIST_SIGNATURE_GUIDE.md) for verification details.