# Release Notes

## [2.1.2] - 2026-01-19

### Fixed

- **Critical**: Fixed infinite loop in `safe_CLI_input()` by adding `max_retries` parameter (default: 10)
- **Critical**: Fixed index offset bug in `insert_at_intervals()` by using reverse insertion
- **Critical**: Replaced hardcoded file size threshold with `LOCK_FILE_SIZE_THRESHOLD` constant (10MB)
- Improved traceback formatting in `ExceptionTracker` using `traceback.format_exception()`

### Added

- JSON serialization support for shared memory IPC (safer alternative to pickle)
  - `GlobalVars.SERIALIZERS` dictionary with pickle and json serialization lambdas
  - `serialize_format` parameter in `shm_sync()` and `shm_update()` methods
- Language cache management with automatic reload on KeyError via `__lang_cache_management__` decorator
- Type validation for `safe_CLI_input()` with `SUPPORTED_TYPES` and `other_type` parameter
- `DecoratorUtils.make_decorator()` method for converting functions to decorator form
- Comprehensive security warnings in all shared memory method docstrings

### Changed

- Improved process pool chunk calculation with `math.ceil()` and `max(1, ...)` to prevent zero chunk size
- Enhanced `_check_executable()` return type hint to `Tuple[bool, Optional[str]]`
- Optimized conditional logging checks throughout codebase
- Updated all shared memory security documentation to explain pickle vs JSON trade-offs

### Security

- **Important**: Added JSON serialization option for untrusted inter-process communication
- **Important**: All shared memory methods now document pickle security risks and JSON alternatives
- Pickle serialization retained as default for performance, JSON available via `serialize_format="json"`

---

## [2.1.1] - 2026-01-18

### Added

- `shm_connect()` method for connecting to existing shared memory objects (for child processes)
- Header-based serialization for robust shared memory data transfer

### Changed

- `is_logging_enabled` → `__is_logging_enabled__` (private attribute) in AppCore, FileManager, Utils
- `shm_close()` now accepts `close_only` parameter to close without unlinking shared memory
- GlobalVars internal logic refactored: direct key checks instead of `exists()` for thread safety and performance
- Conditional logging added to reduce overhead when logging is disabled

---

## [2.1.0] - 2026-01-16

### Added

- Shared Memory IPC support for GlobalVars
  - `shm_gen()`, `shm_sync()`, `shm_update()`, `shm_get()`, `shm_close()`
  - Optional `multiprocessing.Lock` for inter-process synchronization
  - LRU cache for shared memory objects (`shm_cache_management()`)
- Context manager support for GlobalVars (`with gv:`)

### Changed

- `ExceptionTracker.get_exception_info()` params type: `dict` → `Tuple[Tuple, dict]`
