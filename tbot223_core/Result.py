#external Modules
from typing import Any, NamedTuple, Optional

#internal Modules

class ResultUnwrapException(RuntimeError):
    """
    Exception raised when attempting to unwrap a Result that indicates failure or cancellation.
    """
    def __init__(self, error, context, data):
        """
        Initializes the ResultUnwrapException with error details.
        
        Args:
            error (Optional[str]): The error message from the Result.
            context (Optional[str]): The context of the Result.
            data (Any): The data contained in the Result.

        Returns:
            None
            
        Example:
            >>> try:
            >>>     result = Result(success=False, error="Some error", context="TestContext", data=None)
            >>>     result.unwrap()
            >>> except ResultUnwrapException as e:
            >>>     print(e)
            >>> # Output: Cannot unwrap Result: Some error, Context: TestContext, Data:
        """
        super().__init__(f"Cannot unwrap Result: {error}, Context: {context}, Data: {data}")
        self.error = error
        self.context = context
        self.data = data
        
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
        success (Optional[bool]): Indicates whether the operation was successful.
            - True if successful, False is the operation failed.
            - None is cancelled or not executed. (async operations may return None if cancelled)
        error (Optional[str]): Error message if the operation failed.
            - Not a Exception object, just a string description.
        context (Optional[str]): Additional context about the operation.
            - Could include operation name, parameters, or state info.
        data (Any): Data returned from the operation.
            - Can be of any type depending on the operation performed.
            - if operation fails, this sould be error details or None. (core modules always set this to error details on failure)
    """
    success: Optional[bool]
    error: Optional[str]
    context: Optional[str]
    data: Any

    def unwrap(self) -> Any:
        """
        Unwraps the Result to get the data if successful.
        
        Args:
            None

        Returns:
            Any: The unwrapped data if the operation was successful.

        Raises:
            ResultUnwrapException: If the operation was not successful or was cancelled.

        Example:
            >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
            >>> data = result.unwrap()
            >>> print(data)
            >>> # Output: {'key': 'value'}
        """
        if self.success is True:
            return self.data
        elif self.success is False:
            raise ResultUnwrapException(self.error, self.context, self.data)
        else:
            raise ResultUnwrapException("Operation was cancelled or not executed.", self.context, self.data)

    def expect(self) -> Any:
        """
        Unwraps the Result to get the data if successful.
        
        Args:
            None

        Returns:
            Any: The unwrapped data if the operation was successful.

        Raises:
            ResultUnwrapException: If the operation was not successful.

        Example:
            >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
            >>> data = result.expect()
            >>> print(data)
            >>> # Output: {'key': 'value'}
        """
        if self.success is True:
            return self.data
        raise ResultUnwrapException(self.error, self.context, self.data)
    
    def unwrap_or(self, default: Any) -> Any:
        """
        Unwraps the Result to get the data if successful, otherwise returns the default value.
        
        Args:
            None

        Returns:
            Any: The unwrapped data if the operation was successful, otherwise the default value.
        
        Example:
            >>> result = Result(success=False, error="Not Found", context="FetchData", data=None)
            >>> data = result.unwrap_or({"key": "default_value"})
            >>> print(data)
            >>> # Output: {'key': 'default_value'}
        """
        if self.success is True:
            return self.data
        return default