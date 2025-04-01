# Guidelines for Claude

## Project: Todoist-Notion Bidirectional Sync

### Commands
- Build: TBD (project not yet configured)
- Lint: TBD (project not yet configured)
- Test: TBD (project not yet configured)
- Single test: TBD (project not yet configured)

### Code Style Guidelines
- **Language**: Assume Python unless otherwise specified
- **Formatting**: PEP 8 compliant with 88-character line length (Black compatible)
- **Imports**: Group standard library, third-party, and local imports with single line between groups
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Types**: Use type annotations for all function parameters and return values
- **Documentation**: Docstrings for all public classes and functions (Google style)
- **Error Handling**: Use explicit exception handling with specific exception types
- **Logging**: Use Python's logging module for all logging needs
- **Security**: Never store API keys directly in code, use environment variables

### Additional Notes
- Project aims to synchronize tasks between Todoist and Notion
- Configure both Todoist and Notion API authentication via environment variables