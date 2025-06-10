# Todoist-Notion Sync Design Document

## Architecture Overview

This document outlines the design principles and implementation strategy for the Todoist-Notion bidirectional synchronization system.

## Core Principles

1. **Notion as Source of Truth**: Notion serves as the primary source of truth for task data and mappings
2. **Stateless Webhook Processing**: Webhook handlers process events without maintaining state
3. **Robust Deletion Tracking**: Deleted tasks are soft-deleted rather than purged
4. **Simplicity**: Focus on core functionality with minimal complexity

## Identity Mapping Strategy

Rather than maintaining a separate mapping file, we store Todoist IDs directly in the Notion databases:

**Task Mapping:**
- Each Notion task page contains a "Todoist ID" property
- This eliminates a separate point of failure
- Makes the mapping visually auditable in Notion

**Project Mapping:**
- Each Notion area page contains a "Todoist Project ID" property
- Enables bidirectional sync between Todoist projects and Notion areas
- Supports the PARA method's organizational structure

## PARA Method Integration

The system incorporates the PARA (Projects, Areas, Resources, Archives) method for organization:

- **Areas in Notion** map to top-level Todoist projects initially
- **Projects in Notion** will potentially map to Todoist sub-projects in the future
- The relational structure in Notion provides richer organization than Todoist's project hierarchy
- Tasks maintain their relationships across systems through ID mapping

### Current Mapping (Implemented)
- Todoist Project ↔ Notion Area
- Todoist Task ↔ Notion Task
- Task-Area relationships via Notion relations

### Future Mapping (Phase 2)
- Todoist Project ↔ Notion Area
- Todoist Sub-Project ↔ Notion Project
- Todoist Task ↔ Notion Task
- Nested project hierarchies

## Status Mapping

### Task Status Mapping

| Todoist Status | Notion Status |
|----------------|---------------|
| Incomplete (`checked: false`) | Not Started |
| Completed (`checked: true`) | Completed |

### Project Status Mapping

| Todoist State | Notion Area Status | `is_archived` | `is_deleted` | Notion `Deleted` |
|---------------|-------------------|---------------|--------------|------------------|
| Active | Active | `false` | `false` | `false` |
| Archived | Active | `true` | `false` | `false` |
| Deleted | Active | any | `true` | `true` |

**Rationale for Project Mapping:**
- Archived projects remain accessible in Notion (user preference)
- Only hard-deleted projects trigger soft deletion in Notion
- Preserves workflow flexibility between systems

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

The main Tasks database includes these properties:

| Property | Type | Options/Config | Purpose |
|----------|------|----------------|---------|
| **Name** | Title | - | Task title from Todoist `content` |
| **Status** | Select | "Not Started", "Completed" | Task completion status |
| **Priority** | Select | "Normal", "Low", "Medium", "High" | Maps Todoist priorities 1-4 |
| **Due Date** | Date | Include time | Due date with timezone handling |
| **Description** | Rich Text | - | Task description/notes |
| **Labels** | Multi-select | Dynamic | Todoist labels as tags |
| **Area** | Relation | → Areas database | Link to containing area/project |
| **Todoist ID** | Rich Text | - | Unique task identifier for mapping |
| **Todoist Project ID** | Rich Text | - | Reference to source project |
| **Last Synced** | Date | Include time | Timestamp of last sync |
| **Deleted** | Checkbox | - | Soft delete flag |
| **Deleted At** | Date | Include time | When item was deleted |
| **Deleted By** | Select | "Todoist", "Notion" | Which system deleted the item |

### Areas Database (PARA Method)

The Areas database represents ongoing responsibilities and maps to Todoist projects:

| Property | Type | Options/Config | Purpose |
|----------|------|----------------|---------|
| **Name** | Title | - | Area name from Todoist project `name` |
| **Description** | Rich Text | - | Area purpose and details |
| **Color** | Select | Todoist colors | Visual organization aid |
| **Todoist Project ID** | Rich Text | - | Unique project identifier for mapping |
| **Tasks** | Relation | ← Tasks database | Rollup of related tasks |
| **Is Archived** | Checkbox | - | Tracks Todoist archive status |
| **Last Synced** | Date | Include time | Timestamp of last sync |
| **Deleted** | Checkbox | - | Soft delete flag |
| **Deleted At** | Date | Include time | When area was deleted |
| **Deleted By** | Select | "Todoist", "Notion" | Which system deleted the area |

### Projects Database (PARA Method)

The Projects database represents time-bound initiatives (future implementation):

| Property | Type | Options/Config | Purpose |
|----------|------|----------------|---------|
| **Name** | Title | - | Project name |
| **Area** | Relation | → Areas database | Parent area relationship |
| **Status** | Select | "Active", "Completed", "On Hold" | Project lifecycle status |
| **Tasks** | Relation | ← Tasks database | Rollup of project tasks |
| **Start Date** | Date | - | Project initiation date |
| **Target Completion** | Date | - | Planned completion date |
| **Todoist Project ID** | Rich Text | - | Future: sub-project mapping |

**Note:** This database is designed for future enhancement when Todoist sub-project support is added.

## Implementation Phases

### Phase 1: Core Task & Project Sync (Current)
- ✅ Task synchronization (create, update, complete, delete)
- ✅ Project synchronization (create, update, archive, delete)
- ✅ Task-Area relationships via Notion relations
- ✅ Soft deletion with audit trails
- ✅ Priority and label mapping

### Phase 2: Advanced Features (Future)
- **Bidirectional Change Detection**: Compare timestamps to determine which system has the most recent changes
- **Extended Properties Sync**: Sync additional properties like reminders, task hierarchy
- **Project-Task Hierarchy**: Support for Todoist sub-projects mapping to Notion Projects
- **Resources & Archives Integration**: Complete the PARA method with Resources and Archives databases
- **Filtering & Views**: Smart filtering to show only relevant tasks based on contexts
- **Recurring Task Support**: Handle Todoist's recurring task patterns in Notion
- **Batch Synchronization**: Periodic full sync to catch any missed webhook events

## Technical Implementation Notes

### Environment Variables Required
```env
NOTION_API_KEY=secret_xxx
NOTION_TASK_DATABASE_ID=database_id_xxx
NOTION_AREAS_DATABASE_ID=database_id_xxx
TODOIST_CLIENT_SECRET=client_secret_xxx
```

### Webhook Event Handling
- **Task Events**: `item:added`, `item:updated`, `item:completed`, `item:uncompleted`, `item:deleted`
- **Project Events**: `project:added`, `project:updated`, `project:deleted`, `project:archived`, `project:unarchived`

### Error Handling Strategy
- Comprehensive logging for all API operations
- Retry logic with exponential backoff
- Graceful degradation when services unavailable
- Data validation before API calls