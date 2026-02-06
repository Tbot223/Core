# Migration Guide

## Migrating from 2.x to 3.0.0

Version 3.0.0 introduces significant changes to the import system and module structure. This guide will help you update your code.

---

## Import System Changes

### Direct Class Imports

The most significant change is how you import and instantiate classes.

**Before (2.x):**
```python
from tbot223_core import AppCore, FileManager, LogSys
from tbot223_core.Utils import GlobalVars

# Double reference required
app = AppCore.AppCore()
fm = FileManager.FileManager()
logger_manager = LogSys.LoggerManager()
log = LogSys.Log()
gv = GlobalVars.GlobalVars()
```

**After (3.0.0):**
```python
from tbot223_core import AppCore, FileManager, LoggerManager, Log, GlobalVars

# Direct instantiation
app = AppCore()
fm = FileManager()
logger_manager = LoggerManager()
log = Log()
gv = GlobalVars()
```

### Utils Subpackage

The `Utils.py` module has been split into a subpackage with separate files.

**Before (2.x):**
```python
from tbot223_core.Utils import GlobalVars, DecoratorUtils, Utils
```

**After (3.0.0):**
```python
# Option 1: Import from main package (recommended)
from tbot223_core import GlobalVars, DecoratorUtils, Utils

# Option 2: Import from subpackage
from tbot223_core.Utils.GlobalVars import GlobalVars
from tbot223_core.Utils.DecoratorUtils import DecoratorUtils
from tbot223_core.Utils.Utils import Utils
```

---

## Exception API Changes

### mask_tuple Parameter

The `get_exception_info()` and `get_exception_return()` methods now use `mask_tuple` for masking sensitive information.

**Before (2.x):**
```python
tracker = ExceptionTracker()
info = tracker.get_exception_info(error, user_input=data, params=(args, kwargs))
```

**After (3.0.0):**
```python
tracker = ExceptionTracker()
# mask_tuple order: (user_input, params, traceback, computer_info)
info = tracker.get_exception_info(
    error, 
    user_input=data, 
    params=(args, kwargs),
    mask_tuple=(True, False, True, False)  # Masks user_input and traceback
)
```

---

## Result Object Changes

### success Field Type

The `success` field type changed from `bool` to `Optional[bool]`.

| Value | Meaning |
|-------|---------|
| `True` | Operation succeeded |
| `False` | Operation failed |
| `None` | Operation cancelled or not executed |

### New Methods

Result objects now have convenience methods for unwrapping values:

```python
from tbot223_core import FileManager
from tbot223_core.Result import ResultUnwrapException

fm = FileManager()

# unwrap() - Raises exception if not successful
try:
    content = fm.read_file("example.txt").unwrap()
except ResultUnwrapException as e:
    print(f"Failed: {e.error}")

# expect() - Same as unwrap(), raises if not successful
content = fm.read_file("example.txt").expect()

# unwrap_or() - Returns default if not successful
content = fm.read_file("missing.txt").unwrap_or("default content")
```

---

## Quick Migration Checklist

- [ ] Update all class imports to use direct instantiation
- [ ] Replace `LogSys.LoggerManager` with `LoggerManager`
- [ ] Replace `LogSys.Log` with `Log`
- [ ] Update `Utils` imports to use the new subpackage structure
- [ ] Add `mask_tuple` parameter if using exception masking
- [ ] Rename `id_provider()` to `get_unique_id()`
- [ ] Handle `None` value for `Result.success` if using async operations
- [ ] Consider using new `unwrap()`, `expect()`, `unwrap_or()` methods

---

## Compatibility Notes

- Python 3.10 - 3.12 supported
- All existing functionality is preserved
- Old import style `from tbot223_core.Utils.GlobalVars import GlobalVars` still works

---

# 한국어 (Korean)

# 마이그레이션 가이드

## 2.x에서 3.0.0으로 마이그레이션

버전 3.0.0에서는 import 시스템과 모듈 구조에 중요한 변경사항이 도입되었습니다. 이 가이드가 코드 업데이트에 도움이 될 것입니다.

---

## Import 시스템 변경

### 직접 클래스 Import

가장 큰 변경사항은 클래스를 import하고 인스턴스화하는 방식입니다.

**이전 (2.x):**
```python
from tbot223_core import AppCore, FileManager, LogSys
from tbot223_core.Utils import GlobalVars

# 이중 참조 필요
app = AppCore.AppCore()
fm = FileManager.FileManager()
logger_manager = LogSys.LoggerManager()
log = LogSys.Log()
gv = GlobalVars.GlobalVars()
```

**이후 (3.0.0):**
```python
from tbot223_core import AppCore, FileManager, LoggerManager, Log, GlobalVars

# 직접 인스턴스화
app = AppCore()
fm = FileManager()
logger_manager = LoggerManager()
log = Log()
gv = GlobalVars()
```

### Utils 서브패키지

`Utils.py` 모듈이 별도의 파일을 가진 서브패키지로 분리되었습니다.

**이전 (2.x):**
```python
from tbot223_core.Utils import GlobalVars, DecoratorUtils, Utils
```

**이후 (3.0.0):**
```python
# 옵션 1: 메인 패키지에서 import (권장)
from tbot223_core import GlobalVars, DecoratorUtils, Utils

# 옵션 2: 서브패키지에서 import
from tbot223_core.Utils.GlobalVars import GlobalVars
from tbot223_core.Utils.DecoratorUtils import DecoratorUtils
from tbot223_core.Utils.Utils import Utils
```

---

## Exception API 변경

### mask_tuple 파라미터

`get_exception_info()`와 `get_exception_return()` 메서드는 이제 민감한 정보를 마스킹하기 위해 `mask_tuple`을 사용합니다.

**이전 (2.x):**
```python
tracker = ExceptionTracker()
info = tracker.get_exception_info(error, user_input=data, params=(args, kwargs))
```

**이후 (3.0.0):**
```python
tracker = ExceptionTracker()
# mask_tuple 순서: (user_input, params, traceback, computer_info)
info = tracker.get_exception_info(
    error, 
    user_input=data, 
    params=(args, kwargs),
    mask_tuple=(True, False, True, False)  # user_input과 traceback 마스킹
)
```

---

## Result 객체 변경

### success 필드 타입

`success` 필드 타입이 `bool`에서 `Optional[bool]`로 변경되었습니다.

| 값 | 의미 |
|-------|---------|
| `True` | 작업 성공 |
| `False` | 작업 실패 |
| `None` | 작업 취소됨 또는 실행되지 않음 |

### 새로운 메서드

Result 객체에 값을 추출하기 위한 편의 메서드가 추가되었습니다:

```python
from tbot223_core import FileManager
from tbot223_core.Result import ResultUnwrapException

fm = FileManager()

# unwrap() - 성공이 아니면 예외 발생
try:
    content = fm.read_file("example.txt").unwrap()
except ResultUnwrapException as e:
    print(f"실패: {e.error}")

# expect() - unwrap()과 동일, 성공이 아니면 예외 발생
content = fm.read_file("example.txt").expect()

# unwrap_or() - 성공이 아니면 기본값 반환
content = fm.read_file("missing.txt").unwrap_or("기본 내용")
```

---

## 빠른 마이그레이션 체크리스트

- [ ] 모든 클래스 import를 직접 인스턴스화 방식으로 업데이트
- [ ] `LogSys.LoggerManager`를 `LoggerManager`로 교체
- [ ] `LogSys.Log`를 `Log`로 교체
- [ ] `Utils` import를 새로운 서브패키지 구조로 업데이트
- [ ] 예외 마스킹 사용 시 `mask_tuple` 파라미터 추가
- [ ] `id_provider()`를 `get_unique_id()`로 이름 변경
- [ ] 비동기 작업 사용 시 `Result.success`의 `None` 값 처리
- [ ] 새로운 `unwrap()`, `expect()`, `unwrap_or()` 메서드 사용 고려

---

## 호환성 참고사항

- Python 3.10 - 3.12 지원
- 모든 기존 기능 유지
- 이전 import 스타일 `from tbot223_core.Utils.GlobalVars import GlobalVars`도 계속 작동
