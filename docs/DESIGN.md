# Todoist-Notion Sync Design Document

## Architecture Overview

This document outlines the design principles and implementation strategy for the Todoist-Notion bidirectional synchronization system.

## Core Principles

1. **Notion as Source of Truth**: Notion serves as the primary source of truth for task data and mappings
2. **Stateless Webhook Processing**: Webhook handlers process events without maintaining state
3. **Robust Deletion Tracking**: Deleted tasks are soft-deleted rather than purged
4. **Simplicity**: Focus on core functionality with minimal complexity

## Task Identity Mapping

Rather than maintaining a separate mapping file, we store Todoist IDs directly in the Notion database:

- Each Notion page (task) contains a "Todoist ID" property
- This eliminates a separate point of failure
- Makes the mapping visually auditable in Notion

## PARA Method Integration

The system incorporates the PARA (Projects, Areas, Resources, Archives) method for organization:

- **Areas in Notion** map to top-level Todoist projects initially
- **Projects in Notion** will potentially map to Todoist sub-projects in the future
- The relational structure in Notion provides richer organization than Todoist's project hierarchy
- Tasks maintain their relationships across systems through ID mapping

### Current Mapping
- Todoist Project ↔ Notion Area
- Todoist Task ↔ Notion Task

### Future Mapping
- Todoist Project ↔ Notion Area
- Todoist Sub-Project ↔ Notion Project
- Todoist Task ↔ Notion Task

## Status Mapping

We use a simple status mapping between Todoist and Notion:

| Todoist | Notion |
|---------|--------|
| Incomplete | Not Started |
| Completed | Completed |

## Deletion Handling Strategy

Notion should implement the following properties for tracking deletions:

| Property | Type | Purpose |
|----------|------|---------|
| Deleted | Checkbox | Marks an item as deleted |
| Deleted At | Date | Timestamp of deletion |
| Deleted By | Select (Todoist/Notion) | Source of deletion event |

### Benefits of this approach:

1. **No Lost Data**: Items are never fully removed
2. **Audit Trail**: Records of who deleted what and when
3. **Conflict Resolution**: Enables time-based resolution of delete vs update conflicts
4. **Recovery Options**: Supports potential undeletion features

### Implementation Example:

```python
# When handling a deletion from Todoist
def handle_item_deleted(item_data):
    todoist_id = item_data["id"]
    notion_page = find_notion_page_by_todoist_id(todoist_id)
    
    if notion_page:
        update_notion_page(notion_page["id"], {
            "Deleted": True,
            "Deleted At": datetime.now(),
            "Deleted By": "Todoist"
        })
```

## Conflict Resolution

When conflicts occur between systems, we follow these rules:

1. **Creation Conflict**: If both systems created a similar task, maintain separate tasks
2. **Update vs Delete Conflict**: 
   - If update came after delete (within 24h), restore item with updated content
   - If delete came after update, maintain deletion

## Database Schema (Notion)

### Tasks Database

The main Tasks database should include these properties:

- **Name**: Task title (string)
- **Status**: Task status (select: Not Started, Completed)
- **Due Date**: Task due date (date)
- **Description**: Task details (text)
- **Area**: Relation to Areas database
- **Project**: Relation to Projects database
- **Todoist ID**: ID from Todoist (string)
- **Todoist Project ID**: ID of the Todoist project (string)
- **Last Synced**: Timestamp of last sync (date)
- **Deleted**: Soft delete flag (checkbox)
- **Deleted At**: When item was deleted (date)
- **Deleted By**: Which system deleted the item (select)

### Areas Database (PARA Method)

The Areas database represents ongoing responsibilities and maps to top-level Todoist projects:

- **Name**: Area name
- **Todoist Project ID**: ID of corresponding Todoist project
- **Tasks**: Relation to Tasks database (rollup)
- **Description**: Details about this area of responsibility

### Projects Database (PARA Method)

The Projects database represents time-bound initiatives and may map to Todoist sub-projects in the future:

- **Name**: Project name
- **Area**: Relation to the area this project belongs to
- **Status**: Project status (Active, Completed)
- **Todoist Project ID**: ID of corresponding Todoist project/sub-project (for future use)
- **Tasks**: Relation to Tasks database (rollup)
- **Start Date**: When the project started
- **Target Completion**: Target completion date

## Future Enhancements

- **Bidirectional Change Detection**: Compare timestamps to determine which system has the most recent changes
- **Extended Properties Sync**: Sync additional properties like reminders, labels, etc.
- **Project-Task Hierarchy**: Support for Todoist sub-projects mapping to Notion Projects
- **Resources & Archives Integration**: Complete the PARA method with Resources and Archives databases
- **Filtering & Views**: Smart filtering to show only relevant tasks based on contexts
- **Recurring Task Support**: Handle Todoist's recurring task patterns in Notion
- **Batch Synchronization**: Periodic full sync to catch any missed webhook events