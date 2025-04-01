"""Utilities for mapping between Todoist and Notion task IDs."""
import os
import json
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Default path for the mapping file
DEFAULT_MAPPING_PATH = "task_mapping.json"


class TaskMapping:
    """Store and retrieve mappings between Todoist and Notion task IDs."""
    
    def __init__(self, mapping_file: str = DEFAULT_MAPPING_PATH):
        """
        Initialize the task mapping utility.
        
        Args:
            mapping_file: Path to the JSON file that stores the mappings
        """
        self.mapping_file = mapping_file
        self.todoist_to_notion = {}
        self.notion_to_todoist = {}
        self._load_mappings()
    
    def _load_mappings(self) -> None:
        """Load task mappings from the mapping file."""
        if not os.path.exists(self.mapping_file):
            logger.info(f"Mapping file not found at {self.mapping_file}, creating new mapping")
            return
            
        try:
            with open(self.mapping_file, "r") as f:
                mappings = json.load(f)
                
            self.todoist_to_notion = mappings.get("todoist_to_notion", {})
            self.notion_to_todoist = mappings.get("notion_to_todoist", {})
            
            logger.info(f"Loaded {len(self.todoist_to_notion)} task mappings")
        except Exception as e:
            logger.exception(f"Error loading task mappings: {str(e)}")
    
    def _save_mappings(self) -> None:
        """Save task mappings to the mapping file."""
        try:
            mappings = {
                "todoist_to_notion": self.todoist_to_notion,
                "notion_to_todoist": self.notion_to_todoist,
            }
            
            with open(self.mapping_file, "w") as f:
                json.dump(mappings, f, indent=2)
                
            logger.info(f"Saved {len(self.todoist_to_notion)} task mappings")
        except Exception as e:
            logger.exception(f"Error saving task mappings: {str(e)}")
    
    def add_mapping(self, todoist_id: str, notion_id: str) -> None:
        """
        Add a new mapping between a Todoist task and a Notion page.
        
        Args:
            todoist_id: The Todoist task ID
            notion_id: The Notion page ID
        """
        self.todoist_to_notion[todoist_id] = notion_id
        self.notion_to_todoist[notion_id] = todoist_id
        self._save_mappings()
        logger.info(f"Added mapping: Todoist {todoist_id} -> Notion {notion_id}")
    
    def get_notion_id(self, todoist_id: str) -> Optional[str]:
        """
        Get the Notion page ID for a Todoist task.
        
        Args:
            todoist_id: The Todoist task ID
            
        Returns:
            The Notion page ID, or None if no mapping exists
        """
        return self.todoist_to_notion.get(todoist_id)
    
    def get_todoist_id(self, notion_id: str) -> Optional[str]:
        """
        Get the Todoist task ID for a Notion page.
        
        Args:
            notion_id: The Notion page ID
            
        Returns:
            The Todoist task ID, or None if no mapping exists
        """
        return self.notion_to_todoist.get(notion_id)
    
    def remove_mapping_by_todoist(self, todoist_id: str) -> None:
        """
        Remove a mapping by Todoist task ID.
        
        Args:
            todoist_id: The Todoist task ID
        """
        if todoist_id in self.todoist_to_notion:
            notion_id = self.todoist_to_notion[todoist_id]
            del self.todoist_to_notion[todoist_id]
            
            if notion_id in self.notion_to_todoist:
                del self.notion_to_todoist[notion_id]
                
            self._save_mappings()
            logger.info(f"Removed mapping for Todoist task: {todoist_id}")
    
    def remove_mapping_by_notion(self, notion_id: str) -> None:
        """
        Remove a mapping by Notion page ID.
        
        Args:
            notion_id: The Notion page ID
        """
        if notion_id in self.notion_to_todoist:
            todoist_id = self.notion_to_todoist[notion_id]
            del self.notion_to_todoist[notion_id]
            
            if todoist_id in self.todoist_to_notion:
                del self.todoist_to_notion[todoist_id]
                
            self._save_mappings()
            logger.info(f"Removed mapping for Notion page: {notion_id}")


# Create a singleton instance
task_mapping = TaskMapping()