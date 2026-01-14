# tbot223-core

A comprehensive utility package providing core functionalities for Python applications, including file management, logging, error tracking, and various utility functions.

## Features

- **Consistent Result Objects**: All functions return a standardized `Result` object for predictable error handling
- **Robust File Management**: Atomic file operations, JSON handling, and safe file I/O
- **Advanced Logging System**: Structured logging with automatic log file management
- **Exception Tracking**: Detailed error tracking with system information and context
- **Utility Functions**: Encryption, path handling, parallel execution, and more
- **Multi-language Support**: Built-in localization support

## Installation

```bash
pip install tbot223-core
```

## Python Version

Python 3.10 - 3.12

## Core Modules

### AppCore
Provides core application functionalities including:
- Parallel execution (thread/process pools)
- Console management (clear console)
- Application lifecycle control (restart, exit)
- Localization support (multi-language text retrieval)
- Safe CLI input with validation and type conversion

### FileManager
Safe and reliable file operations:
- Atomic file writing
- File read operations (text and binary modes)
- JSON read/write operations
- File/directory listing with extension filtering
- File/directory existence checking
- Safe file/directory deletion
- Directory creation with parent support
- Cross-platform file locking

### LogSys
Structured logging system:
- Logger management with automatic file organization
- Time-stamped log files
- Configurable log levels
- Centralized log instances

### Utils
Collection of utility functions:
- Path conversions
- Encryption (md5, sha1, sha256, sha512)
- PBKDF2 HMAC hash generation and verification
- List/string manipulation (insert at intervals)
- Dictionary operations (find keys by value with comparison operators)

#### GlobalVars
Thread-safe global variable management:
- Set, get, and delete variables
- Variable existence checking
- List all variables
- Attribute access syntax support
- Call syntax for get/set operations

#### DecoratorUtils
Utility decorators:
- Runtime measurement decorator

### ExceptionTracker
Comprehensive error tracking:
- Exception location tracking (file, line, function)
- System information caching (OS, architecture, Python version)
- Detailed error context with timestamps and traceback
- Information masking support for sensitive data
- Decorator for automatic exception handling

## Result Object

All functions (except internal ones) return a `Result` NamedTuple for consistent error handling:

```python
Result(
    success: bool,           # Operation success status
    error: Optional[str],    # Error message if failed
    context: Optional[str],  # Additional context information
    data: Any               # Returned data
)
```

### Usage Example

```python
from tbot223_core import FileManager

fm = FileManager.FileManager()
result = fm.read_file("example.txt")

if result.success:
    print(f"File content: {result.data}")
else:
    print(f"Error: {result.error}")
```

## Error Information

System information is cached when library classes are instantiated. Access detailed error information via `Result.data`:

```python
{
    "success": bool,
    "error": {
        "type": "ExceptionType",
        "message": "Exception message"
    },
    "location": {
        "file": "filename",
        "line": 123,
        "function": "function_name"
    },
    "timestamp": "YYYY-MM-DD HH:MM:SS",
    "input_context": {
        "user_input": "...",
        "params": {...}
    },
    "traceback": "Full traceback...",
    "computer_info": {
        "OS": "OS name",
        "OS_version": "OS version",
        "Release": "OS release",
        "Architecture": "Machine architecture",
        "Processor": "Processor information",
        "Python_Version": "Python version",
        "Python_Executable": "Path to Python executable",
        "Current_Working_Directory": "Current working directory"
    }
}
```

## Quick Start

```python
from tbot223_core import AppCore, FileManager

app = AppCore.AppCore(
    is_logging_enabled=True,
    is_debug_enabled=False,
    default_lang="en"
)

filemanager = FileManager.FileManager(
    is_logging_enabled=True,
    is_debug_enabled=False,
    # Empty space (set as CWD) or custom path
    base_dir=""
)

# Use FileManager for safe file operations
result = filemanager.write_json("config.json", {"key": "value"})

# Execute functions in parallel
tasks = [
    (somefunc, {"some_arg1": val1}),
    (anotherfunc, {"some_arg1": val1, "some_arg1": val2})
]
result = app.thread_pool_executor(tasks, workers=4)
```

## License

Apache License 2.0

## Links

- GitHub: https://github.com/Tbot223/Core
- Author: tbot223 (tbotxyz@gmail.com)