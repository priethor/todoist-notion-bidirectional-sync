"""Complete setup validator for both Todoist and Notion integration."""
import os
import logging
import argparse
from typing import Dict, Any

from .notion.validator import NotionValidator

logger = logging.getLogger(__name__)


class TodoistValidator:
    """Validates Todoist webhook configuration."""
    
    def __init__(self):
        """Initialize the Todoist validator."""
        self.client_secret = os.getenv("TODOIST_CLIENT_SECRET", "").strip()
        
    def validate_all(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Run all Todoist validation checks.
        
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
            print("🔍 Todoist Setup Validation")
            print("=" * 40)
        
        # Check 1: Environment variables
        if verbose:
            print("Checking Todoist environment variables...")
        env_check = self._check_environment()
        results["checks"]["environment"] = env_check
        if verbose:
            emoji = "✅" if env_check["success"] else "❌"
            print(f"  {emoji} Environment: {env_check['message']}")
        if not env_check["success"]:
            results["overall_status"] = "FAIL"
            
        # Check 2: Client secret format
        if verbose:
            print("Validating client secret format...")
        secret_check = self._check_client_secret_format()
        results["checks"]["client_secret"] = secret_check
        if verbose:
            emoji = "✅" if secret_check["success"] else "❌"
            print(f"  {emoji} Client Secret: {secret_check['message']}")
        if not secret_check["success"]:
            results["overall_status"] = "FAIL"
            
        return results
        
    def _check_environment(self) -> Dict[str, Any]:
        """Check if Todoist environment variables are set."""
        if not self.client_secret:
            return {
                "success": False,
                "message": "TODOIST_CLIENT_SECRET not set. Get from Todoist Developer Console."
            }
        else:
            return {
                "success": True,
                "message": "Todoist environment variables are set"
            }
            
    def _check_client_secret_format(self) -> Dict[str, Any]:
        """Validate client secret format."""
        if not self.client_secret:
            return {
                "success": False,
                "message": "No client secret to validate"
            }
            
        # Todoist client secrets are typically 32-character hex strings
        if len(self.client_secret) == 32 and all(c in '0123456789abcdef' for c in self.client_secret.lower()):
            return {
                "success": True,
                "message": "Client secret format is valid"
            }
        else:
            return {
                "success": False,
                "message": "Client secret format looks invalid. Should be 32-character hex string."
            }


class SetupValidator:
    """Complete setup validator for Todoist-Notion integration."""
    
    def __init__(self, auto_fix: bool = False):
        """Initialize the complete validator."""
        self.notion_validator = NotionValidator(auto_fix=auto_fix)
        self.todoist_validator = TodoistValidator()
        self.auto_fix = auto_fix
        
    def validate_all(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Run complete validation for both services.
        
        Args:
            verbose: Print progress in real-time
        
        Returns:
            Dict with validation results and status
        """
        if verbose:
            print("🚀 Complete Integration Setup Validation")
            print("=" * 50)
            print()
        
        # Validate Todoist setup
        todoist_results = self.todoist_validator.validate_all(verbose=verbose)
        
        if verbose:
            print()
        
        # Validate Notion setup
        notion_results = self.notion_validator.validate_all(verbose=verbose)
        
        # Combine results
        overall_status = "PASS" if (todoist_results["overall_status"] == "PASS" and 
                                   notion_results["overall_status"] == "PASS") else "FAIL"
        
        results = {
            "overall_status": overall_status,
            "todoist": todoist_results,
            "notion": notion_results
        }
        
        if verbose:
            print("\n" + "=" * 50)
            status_emoji = "✅" if overall_status == "PASS" else "❌"
            print(f"Complete Setup Status: {status_emoji} {overall_status}")
            
            if overall_status == "PASS":
                print("🎉 Complete setup validation passed!")
                print("📋 Next steps:")
                print("   1. Set up Todoist webhook (see WEBHOOK_SETUP.md)")
                print("   2. Test integration by creating a task in Todoist")
                print("   3. Verify it appears in your Notion database")
            else:
                print("⚠️  Please fix the issues above before proceeding.")
                print("📖 Check setup documentation:")
                print("   - Notion: NOTION_SETUP.md")
                print("   - Todoist: WEBHOOK_SETUP.md")
        
        return results
        
    def print_validation_report(self) -> None:
        """Print a complete validation report."""
        self.validate_all(verbose=True)


# Convenience functions
def validate_complete_setup() -> bool:
    """
    Quick validation function for complete setup.
    
    Returns:
        True if all checks pass, False otherwise
    """
    validator = SetupValidator()
    results = validator.validate_all(verbose=False)
    return results["overall_status"] == "PASS"


def validate_todoist_setup() -> bool:
    """
    Quick validation function for Todoist setup.
    
    Returns:
        True if all checks pass, False otherwise
    """
    validator = TodoistValidator()
    results = validator.validate_all(verbose=False)
    return results["overall_status"] == "PASS"


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Validate Todoist-Notion integration setup')
    parser.add_argument('--auto-fix', action='store_true', 
                       help='Automatically create missing database properties')
    args = parser.parse_args()
    
    # Run complete validation with auto-fix option
    validator = SetupValidator(auto_fix=args.auto_fix)
    validator.print_validation_report()