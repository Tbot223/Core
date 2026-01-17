# Release Notes

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
