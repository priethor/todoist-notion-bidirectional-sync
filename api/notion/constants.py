"""Constants for Notion database properties and values."""
from enum import Enum

# Notion property names - Tasks Database
class TaskProperties:
    NAME = "Name"
    TODOIST_ID = "Todoist ID"
    STATUS = "Status"
    PRIORITY = "Priority"
    DUE_DATE = "Due Date"
    DESCRIPTION = "Description"
    LABELS = "Labels"
    AREA = "Area"
    TODOIST_PROJECT_ID = "Todoist Project ID"
    DELETED = "Deleted"
    DELETED_AT = "Deleted At"
    DELETED_BY = "Deleted By"

# Notion property names - Areas Database
class AreaProperties:
    NAME = "Name"
    TODOIST_PROJECT_ID = "Todoist Project ID"
    DESCRIPTION = "Description"
    TASKS = "Tasks"
    IS_ARCHIVED = "Is Archived"
    DELETED = "Deleted"
    DELETED_AT = "Deleted At"
    DELETED_BY = "Deleted By"

# Status values for Tasks
class TaskStatus:
    NOT_STARTED = "Not Started"
    COMPLETED = "Completed"

# Priority values for Tasks (using Todoist numeric values)
class TaskPriority(Enum):
    NORMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    
    def __str__(self) -> str:
        return self.name.title()

# Deletion source values
class DeletionSource:
    TODOIST = "Todoist"
    NOTION = "Notion"

# Now we can use TaskPriority(todoist_priority) directly!