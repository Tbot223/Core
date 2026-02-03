
# TODO: Exception Module whole review and refactor needed
# TODO: All Methods need re-structuring and optimization
# Why? -> It's So old. So, it's not optimized, and not structured well.
# TODO: Add tb[0] info to get the origin of exception (currently using tb[-1] only)
# Why? -> To provide more detailed exception origin information.
# WARNING: Method names DO NOT change ( Arguments are allowed to change )
# Why? -> To maintain backward compatibility.
# TODO: Add unique ID provider for exceptions (for future use)
# Why? -> To uniquely identify exceptions for tracking and logging.
# TODO: All Moudules need to be re-checked for use of ExceptionTracker
# Why? -> To ensure consistent exception handling across the codebase.

# external modules
import sys
import os
import platform
import time
import traceback
from typing import Any, Tuple

# internal modules
from tbot223_core.Result import Result

class ExceptionTracker():
    """
    The ExceptionTracker class provides functionality to track location information when exceptions occur and return related information.
    
    1. Exception Location Tracking: Provides functionality to track where exceptions occur and return related information.
        - get_exception_location: Returns the location where the exception occurred.

    2. Exception Information Tracking: Provides functionality to track exception information and return related information.
        - get_exception_info: Returns information about the exception.
    """

    def __init__(self):
        # Cache system information
        # Safely get current working directory
        try:
            cwd = os.getcwd()
        except Exception:
            cwd = "<Permission Denied or Unavailable>"

        self._system_info = {
            "OS": platform.system(),
            "OS_version": platform.version(),
            "Release": platform.release(),
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
            "Python_Version": platform.python_version(),
            "Python_Executable": sys.executable,
            "Current_Working_Directory": cwd
        }

    # L1 Methods
    def get_exception_location(self, error: Exception) -> Result:
        """
        Function to track where exceptions occurred and return related information

        Args:
            - error (Exception): The exception object to track.

        Returns:
            Result: A Result object containing the location information where the exception occurred.
                - Format (str): '{file}', line {line}, in {function}'

        Example:
            >>> try:
            >>>     1 / 0
            >>> except Exception as e:
            >>>     location_result = tracker.get_exception_location(e)
            >>>     print(location_result.data)
            >>> # Output: 'script.py', line 10, in <module>
        """
        try:
            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # Most recent frame
            return Result(True, None, None, f"'{frame.filename}', line {frame.lineno}, in {frame.name}")
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_location, L1", tb_str)

    # L2 Methods
    def get_exception_info(self, error: Exception, user_input: Any=None, params: Tuple[Tuple, dict]=None, mask_tuple: Tuple[bool, ...] = ()) -> Result:
        """
        Function to track exception information and return related information
        
        The error data dict includes traceback, location information, occurrence time, input context, etc.
        If masking is True, computer information will be masked.

        Args:
            - error : The exception object to track.
            - user_input : User input context related to the exception. Defaults to None.
            - params : Additional parameters related to the exception. Defaults to None. expected format: (args, kwargs)
            - mask_tuple : A tuple of booleans indicating which parts of the error information to mask. Defaults to an empty tuple.

        Note:
            The mask_tuple should be in the order of ("user_input", "params", "traceback", "computer_info").
            If an element in the tuple is True, the corresponding part of the error information will be masked.
            e.g., mask_tuple = (True, False, True, False) will mask "user_input" and "traceback".

        Returns:
            Result: A Result object containing detailed information about the exception.
                - data (dict): A dictionary containing detailed exception information. ( Please see Readme.md for more details on the structure of error_info )

        Example:
            >>> try:
            >>>     def divide(a, b):
            >>>         return a / b
            >>>     a, b = 10, 0
            >>>     # This will raise a ZeroDivisionError
            >>>     divide(a, b)
            >>> except Exception as e:
            >>>     info_result = tracker.get_exception_info(e, user_input="Divide operation", params=((a, b), {"a":a, "b":b}), mask_tuple=(False, False, False, False))
            >>>     print(info_result.data)
            >>> # Output: ( error_info dict, see Readme.md for structure )
        """
        try:
            if error is None:
                raise ValueError("The 'error' argument must be an Exception instance, not None.")
            if isinstance(params[0], tuple) is False or isinstance(params[1], dict) is False:
                raise ValueError("The 'params' argument must be a tuple of (args, kwargs).")
            if not isinstance(mask_tuple, tuple) or not all(isinstance(i, bool) for i in mask_tuple):
                raise ValueError("The 'mask_tuple' argument must be a tuple of booleans.")
            if len(mask_tuple) != 4:
                raise ValueError("The 'mask_tuple' argument must have exactly 4 boolean values.")

            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # Most recent frame

            masking = lambda index, return_value: "<Masked>" if mask_tuple[index] else return_value

            error_info = {
                "success": False,
                "error":{
                    "type": type(error).__name__ if error else "UnknownError", 
                    "message": str(error) if error else "No exception information available"
                },
                "location": {
                    "file": frame.filename if frame else "Unknown",
                    "line": frame.lineno if frame else -1,
                    "function": frame.name if frame else "Unknown"
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "input_context": {
                    "user_input": masking(0, user_input),
                    "params": masking(1, {
                        "args": params[0] if params else (),
                        "kwargs": params[1] if params else {}
                    }) 
                },
                "id": None,  # Reserved for future use (to provide unique IDs for exceptions)
                "traceback": masking(2, ''.join(traceback.format_exception(type(error), error, error.__traceback__))),
                "computer_info": masking(3, self._system_info)
            }
            return Result(True, None, None, error_info)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_info, L1", tb_str)
    
    # L2 Methods
    def get_exception_return(self, error: Exception, user_input: Any=None, params: Tuple[Tuple, dict]=None, mask_tuple: Tuple[bool, ...]=()) -> Result:
        """
        A convenience function to standardize the return of exception information. It's designed to be used in exception handling blocks.
        ( Includes exception type, message, location, and detailed info. )

        I recommend that the caller return the return value of this function as is.

        If masking is True, Exception information will be masked.

        Args:
            - error : The exception object to track.
            - user_input : User input context related to the exception. Defaults to None.
            - params : Additional parameters related to the exception. Defaults to None. expected format: (args, kwargs)
            - mask_tuple : A tuple of booleans indicating which parts of the error information to mask. Defaults to an empty tuple.

        Note:
            The mask_tuple should be in the order of ("user_input", "params", "traceback", "computer_info").
            If an element in the tuple is True, the corresponding part of the error information will be masked.
            e.g., mask_tuple = (True, False, True, False) will mask "user_input" and "traceback".

        Returns:
            Result: A dictionary containing detailed information about the exception.

        Example:
            >>> try:
            >>>     1 / 0
            >>> except Exception as e:
            >>>     print(tracker.get_exception_return(e, user_input="Divide operation", params=((1, 0), {"a":1, "b":0}), True))
            >>> Result(False, 'ZeroDivisionError :division by zero', "'script.py', line 10, in <module>", '<Masked>')
        """
        try:
            effective_mask = mask_tuple if len(mask_tuple) == 4 else (False, False, False, False)
            return Result(False, f"{type(error).__name__} :{str(error)}", self.get_exception_location(error).data, self.get_exception_info(error, user_input, params, mask_tuple=effective_mask).data)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_return, L2", tb_str)
    
    def get_unique_id(self):
        pass # TODO: Method to provide unique IDs for exceptions (for future use)
        
class ExceptionTrackerDecorator():
    """
    Decorator for wrapping functions with ExceptionTracker.

    - Tracks exceptions and returns a safe value via ExceptionTracker.
    - Use only for non-critical functions (adds overhead).
    - Not suitable if logging or side effects are required. 
    
    Args:
        - masking (bool, optional): If True, exception information will be masked. Defaults to False.
        - tracker (ExceptionTracker, optional): An instance of ExceptionTracker to use. If None, a new instance will be created. Defaults to None.

    Returns:
        If no exception occurs, returns the original function's return value.
        If an exception occurs, returns a Result object with exception details.
    
    Example:
        >>> tracker = ExceptionTracker()
        >>> @ExceptionTrackerDecorator(masking=True, tracker=tracker)
        >>> def risky_function(x, y):
        >>>     return x / y
        >>> print(risky_function(10, y=0))
        >>> # Output: Result(False, 'ZeroDivisionError :division by zero', "'script.py', line 10, in risky_function", '<Masked>')
        >>> print(risky_function(10, y=0).data['params'])
        >>> # Output: ((10,), {'y': 0})
    """
    def __init__(self, masking: bool=False, tracker: ExceptionTracker=None):
        self.tracker = tracker or ExceptionTracker()
        self.masking = masking

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # When masking=True, mask all fields; otherwise mask nothing
                mask_tuple = (True, True, True, True) if self.masking else (False, False, False, False)
                return self.tracker.get_exception_return(error=e, params=(args, kwargs), mask_tuple=mask_tuple)
        return wrapper