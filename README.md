# tbot223-core

A comprehensive utility package providing core functionalities for Python applications, including file management, logging, error tracking, and various utility functions.

## Features

- **Consistent Result Objects**: All functions return a standardized `Result` object for predictable error handling
- **Robust File Management**: Atomic file operations, JSON handling, and safe file I/O
- **Advanced Logging System**: Structured logging with automatic log file management
- **Exception Tracking**: Detailed error tracking with system information and context
- **Utility Functions**: Encryption, path handling, parallel execution, and more
- **Multi-language Support**: Built-in localization support
- **Shared Memory IPC**: Inter-process communication via shared memory with process-safe locking

## Installation

```bash
pip install tbot223-core
```

## Python Version

Python 3.10 - 3.12

## Core Modules

### AppCore
Provides core application functionalities:
- Parallel execution with `ThreadPoolExecutor` / `ProcessPoolExecutor`
- Console management (`clear_console()`)
- Application lifecycle control (`restart_application()`, `exit_application()`)
- Multi-language text retrieval (`get_text_by_lang()`)
- Safe CLI input with validation and type conversion

### FileManager
Safe and reliable file operations:
- Atomic file writing (`atomic_write()`)
- File read operations (`read_file()`) with text/binary modes
- JSON read/write operations (`read_json()`, `write_json()`)
- File/directory listing with extension filtering (`list_of_files()`)
- File/directory existence checking
- Safe file/directory deletion (`delete_file()`, `delete_directory()`)
- Directory creation with parent support (`create_directory()`)
- Cross-platform file locking (`_lock()`)

### LogSys
Structured logging system:
- Logger management with automatic file organization (`LoggerManager`)
- Time-stamped log files
- Configurable log levels
- Centralized log instances (`Log`)
- Simple setup helper (`SimpleSetting`)

### Utils
Collection of utility functions:
- Path conversions (`str_to_path()`)
- Encryption (`encrypt()`) - md5, sha1, sha256, sha512
- PBKDF2 HMAC hash generation and verification (`pbkdf2_hmac()`, `verify_pbkdf2_hmac()`)
- List/string manipulation (`insert_at_intervals()`)
- Dictionary operations (`find_keys_by_value()`) with comparison operators

### GlobalVars
Thread-safe global variable management with shared memory support:
- Variable operations (`set()`, `get()`, `delete()`, `clear()`)
- Variable existence checking (`exists()`, `list_vars()`)
- Attribute access syntax support (`gv.key = value`)
- Call syntax for get/set operations (`gv("key", value)`)
- Shared memory creation (`shm_gen()`) with optional `multiprocessing.Lock`
- Shared memory connection for child processes (`shm_connect()`)
- Shared memory synchronization (`shm_sync()`, `shm_update()`)
- Shared memory access with LRU cache (`shm_get()`, `shm_cache_management()`)
- Shared memory cleanup (`shm_close()`) with optional `close_only` mode
- Context manager support (`with gv:`) for thread-safe operations
- Internal thread lock access (`lock()`)

### DecoratorUtils
Utility decorators:
- Runtime measurement decorator (`runtime()`)

### ExceptionTracker
Comprehensive error tracking:
- Exception location tracking (`get_exception_location()`)
- Detailed exception info with system context (`get_exception_info()`)
- Standardized exception return (`get_exception_return()`)
- System information caching (OS, architecture, Python version)
- Information masking support for sensitive data
- Decorator for automatic exception handling (`ExceptionTrackerDecorator`)

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

## Shared Memory Usage

```python
from tbot223_core.Utils import GlobalVars
from multiprocessing import Process

# Worker function (must be defined at module level)
def worker(shm_name, lock):
    gv_worker = GlobalVars()
    with lock:
        gv_worker.shm_update(shm_name)
        current = gv_worker.get("counter").data
        gv_worker.set("counter", current + 1, overwrite=True)
        gv_worker.shm_sync(shm_name)

if __name__ == "__main__":
    # Main process - all setup must be inside __main__ guard
    gv = GlobalVars()
    result = gv.shm_gen("my_shm", size=4096, create_lock=True)
    shm_lock = result.data  # Get the lock for inter-process sync

    gv.set("counter", 0, overwrite=True)
    gv.shm_sync("my_shm")

    # Start processes (lock must be passed before fork/spawn)
    processes = [Process(target=worker, args=("my_shm", shm_lock)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    # Check result
    gv.shm_update("my_shm")
    print(f"Final counter: {gv.get('counter').data}")  # Output: 4

    # Cleanup
    gv.shm_close("my_shm")
```

## License

Apache License 2.0

## Links

- GitHub: https://github.com/Tbot223/Core
- Author: tbot223 (tbotxyz@gmail.com)