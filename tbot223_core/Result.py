#external Modules
from typing import Any, NamedTuple, Optional

#internal Modules

class Result(NamedTuple):
    """
    Immutable container representing the outcome of an operation in CoreV2.

    This Result type is implemented as a NamedTuple to ensure immutability:
    once created, its attributes cannot be modified. This design helps
    maintain the integrity of operation results and prevents accidental
    state changes across application layers.

    NamedTuple was chosen because it:
    - Guarantees immutability by design
    - Supports attribute access by name for improved readability
    - Is lightweight and memory-efficient compared to regular classes

    Attributes:
        success (bool): Indicates whether the operation was successful.
        error (Optional[str]): Error message if the operation failed.
        context (Optional[str]): Additional context about the operation.
        data (Any): Data returned from the operation.
    """
    success: bool
    error: Optional[str]
    context: Optional[str]
    data: Any