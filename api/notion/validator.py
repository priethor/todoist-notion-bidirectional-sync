"""Notion setup validator to test API connection and database configuration."""
import os
import logging
from typing import Dict, Any, Optional, Tuple, List

from .constants import TaskProperties, AreaProperties

try:
    from notion_client import Client as NotionClient
    NOTION_SDK_AVAILABLE = True
except ImportError:
    NOTION_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

# Required properties for validation
REQUIRED_TASK_PROPERTIES = {
    TaskProperties.NAME: "title",
    TaskProperties.TODOIST_ID: "rich_text", 
    TaskProperties.STATUS: "status",
    TaskProperties.AREA: "relation"
}

REQUIRED_AREA_PROPERTIES = {
    AreaProperties.NAME: "title",
    AreaProperties.TODOIST_ID: "rich_text",
    AreaProperties.TASKS: "relation"
}


class NotionValidator:
    """Validates Notion API connection and database setup."""
    
    def __init__(self):
        """Initialize the validator."""
        self.api_key = os.getenv("NOTION_API_KEY", "").strip()
        self.task_db_id = os.getenv("NOTION_TASK_DATABASE_ID", "").strip()
        self.areas_db_id = os.getenv("NOTION_AREAS_DATABASE_ID", "").strip()
        self.client = None
        
    def validate_all(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Run all validation checks.
        
        Args:
            verbose: Print progress in real-time
        
        Returns:
            Dict with validation results and status
        """
        results = {
            "overall_status": "PASS",
            "checks": {}
        }
        
        if verbose:
            print("🔍 Notion Setup Validation")
            print("=" * 40)
        
        # Check 1: SDK availability
        if verbose:
            print("Checking Notion SDK installation...")
        sdk_check = self._check_sdk()
        results["checks"]["sdk"] = sdk_check
        if verbose:
            emoji = "✅" if sdk_check["success"] else "❌"
            print(f"  {emoji} SDK: {sdk_check['message']}")
        if not sdk_check["success"]:
            results["overall_status"] = "FAIL"
            return results
            
        # Check 2: Environment variables
        if verbose:
            print("Checking environment variables...")
        env_check = self._check_environment()
        results["checks"]["environment"] = env_check
        if verbose:
            emoji = "✅" if env_check["success"] else "❌"
            print(f"  {emoji} Environment: {env_check['message']}")
        if not env_check["success"]:
            results["overall_status"] = "FAIL"
            return results
            
        # Check 3: API connection
        if verbose:
            print("Testing API connection...")
        api_check = self._check_api_connection()
        results["checks"]["api_connection"] = api_check
        if verbose:
            emoji = "✅" if api_check["success"] else "❌"
            print(f"  {emoji} API Connection: {api_check['message']}")
        if not api_check["success"]:
            results["overall_status"] = "FAIL"
            return results
            
        # Check 4: Database access
        if verbose:
            print("Checking database access...")
        db_check = self._check_database_access()
        results["checks"]["database_access"] = db_check
        if verbose:
            emoji = "✅" if db_check["success"] else "❌"
            print(f"  {emoji} Database Access: {db_check['message']}")
            if "details" in db_check:
                for db_name, db_result in db_check["details"].items():
                    db_emoji = "✅" if db_result["accessible"] else "❌"
                    print(f"    {db_emoji} {db_name.replace('_', ' ').title()}: {db_result['message']}")
        if not db_check["success"]:
            results["overall_status"] = "FAIL"
            return results
            
        # Check 5: Database properties
        if verbose:
            print("Validating database properties...")
        props_check = self._check_database_properties()
        results["checks"]["database_properties"] = props_check
        if verbose:
            emoji = "✅" if props_check["success"] else "❌"
            print(f"  {emoji} Database Properties: {props_check['message']}")
            if "details" in props_check:
                for db_name, db_result in props_check["details"].items():
                    db_emoji = "✅" if db_result["valid"] else "❌"
                    print(f"    {db_emoji} {db_name.replace('_', ' ').title()}: {db_result['message']}")
        if not props_check["success"]:
            results["overall_status"] = "FAIL"
            
        return results
        
    def _check_sdk(self) -> Dict[str, Any]:
        """Check if Notion SDK is available."""
        if NOTION_SDK_AVAILABLE:
            return {
                "success": True,
                "message": "Notion SDK is available"
            }
        else:
            return {
                "success": False,
                "message": "Notion SDK not installed. Run: pip install notion-client"
            }
            
    def _check_environment(self) -> Dict[str, Any]:
        """Check if all required environment variables are set."""
        missing = []
        
        if not self.api_key:
            missing.append("NOTION_API_KEY")
        if not self.task_db_id:
            missing.append("NOTION_TASK_DATABASE_ID")
        if not self.areas_db_id:
            missing.append("NOTION_AREAS_DATABASE_ID")
            
        if missing:
            return {
                "success": False,
                "message": f"Missing environment variables: {', '.join(missing)}"
            }
        else:
            return {
                "success": True,
                "message": "All environment variables are set"
            }
            
    def _check_api_connection(self) -> Dict[str, Any]:
        """Test API connection by listing users."""
        try:
            self.client = NotionClient(auth=self.api_key)
            
            # Try to list users to test authentication
            response = self.client.users.list()
            
            return {
                "success": True,
                "message": "Successfully connected to Notion API"
            }
            
        except Exception as e:
            error_msg = str(e)
            if "Unauthorized" in error_msg or "401" in error_msg:
                return {
                    "success": False,
                    "message": "Invalid API key. Check your NOTION_API_KEY."
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to connect to Notion API: {error_msg}"
                }
                
    def _check_database_access(self) -> Dict[str, Any]:
        """Test access to both databases."""
        if not self.client:
            return {
                "success": False,
                "message": "No API connection available"
            }
            
        results = {
            "success": True,
            "message": "Database access validated",
            "details": {}
        }
        
        # Test Tasks database
        task_result = self._test_database_access("Tasks", self.task_db_id)
        results["details"]["tasks_db"] = task_result
        
        # Test Areas database  
        areas_result = self._test_database_access("Areas", self.areas_db_id)
        results["details"]["areas_db"] = areas_result
        
        # Overall success if both databases are accessible
        if not task_result["accessible"] or not areas_result["accessible"]:
            results["success"] = False
            results["message"] = "One or more databases are not accessible"
            
        return results
        
    def _test_database_access(self, name: str, db_id: str) -> Dict[str, Any]:
        """Test access to a specific database."""
        try:
            # Try to retrieve database info
            database = self.client.databases.retrieve(database_id=db_id)
            
            # Try to query the database (limit 1 to minimize impact)
            query_result = self.client.databases.query(
                database_id=db_id,
                page_size=1
            )
            
            return {
                "accessible": True,
                "database_title": database.get("title", [{}])[0].get("plain_text", "Unknown"),
                "properties_count": len(database.get("properties", {})),
                "message": f"{name} database is accessible"
            }
            
        except Exception as e:
            error_msg = str(e)
            if "Could not find database" in error_msg or "object_not_found" in error_msg:
                return {
                    "accessible": False,
                    "message": f"{name} database not found. Check database ID or share database with integration."
                }
            elif "Forbidden" in error_msg or "403" in error_msg or "unauthorized" in error_msg:
                return {
                    "accessible": False,
                    "message": f"No permission to access {name} database. Go to database → Share → Invite your integration with edit permissions."
                }
            elif "path failed validation" in error_msg or "valid uuid" in error_msg:
                return {
                    "accessible": False,
                    "message": f"Invalid {name} database ID format. Should be 32 characters without hyphens."
                }
            else:
                return {
                    "accessible": False,
                    "message": f"Error accessing {name} database: {error_msg}"
                }
                
    def _check_database_properties(self) -> Dict[str, Any]:
        """Check that databases have the required properties."""
        if not self.client:
            return {
                "success": False,
                "message": "No API connection available"
            }
            
        results = {
            "success": True,
            "message": "All required properties found",
            "details": {}
        }
        
        # Check Tasks database properties
        task_props = self._validate_database_properties(
            "Tasks", self.task_db_id, REQUIRED_TASK_PROPERTIES
        )
        results["details"]["tasks_db"] = task_props
        
        # Check Areas database properties  
        area_props = self._validate_database_properties(
            "Areas", self.areas_db_id, REQUIRED_AREA_PROPERTIES
        )
        results["details"]["areas_db"] = area_props
        
        # Overall success if both have required properties
        if not task_props["valid"] or not area_props["valid"]:
            results["success"] = False
            results["message"] = "Missing required properties in one or more databases"
            
        return results
        
    def _validate_database_properties(self, name: str, db_id: str, required_props: Dict[str, str]) -> Dict[str, Any]:
        """Validate that a database has the required properties with correct types."""
        try:
            # Get database schema
            database = self.client.databases.retrieve(database_id=db_id)
            db_properties = database.get("properties", {})
            
            missing_props = []
            wrong_type_props = []
            
            for prop_name, expected_type in required_props.items():
                if prop_name not in db_properties:
                    missing_props.append(prop_name)
                else:
                    actual_type = db_properties[prop_name].get("type")
                    if actual_type != expected_type:
                        wrong_type_props.append(f"{prop_name} (expected {expected_type}, got {actual_type})")
            
            if missing_props or wrong_type_props:
                error_parts = []
                if missing_props:
                    error_parts.append(f"Missing: {', '.join(missing_props)}")
                if wrong_type_props:
                    error_parts.append(f"Wrong type: {', '.join(wrong_type_props)}")
                    
                return {
                    "valid": False,
                    "message": f"{'; '.join(error_parts)}"
                }
            else:
                return {
                    "valid": True,
                    "message": f"{name} database has all required properties"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "message": f"Error checking {name} database properties: {str(e)}"
            }
                
    def print_validation_report(self) -> None:
        """Print a formatted validation report with real-time progress."""
        results = self.validate_all(verbose=True)
        
        # Print final status
        print("\n" + "=" * 40)
        status_emoji = "✅" if results["overall_status"] == "PASS" else "❌"
        print(f"Overall Status: {status_emoji} {results['overall_status']}")
        
        if results["overall_status"] == "PASS":
            print("🎉 Setup validation passed! Ready to sync with Todoist.")
        else:
            print("⚠️  Please fix the issues above before proceeding.")


# Convenience function for quick validation
def validate_notion_setup() -> bool:
    """
    Quick validation function.
    
    Returns:
        True if all checks pass, False otherwise
    """
    validator = NotionValidator()
    results = validator.validate_all()
    return results["overall_status"] == "PASS"


if __name__ == "__main__":
    # Run validation when script is executed directly
    validator = NotionValidator()
    validator.print_validation_report()