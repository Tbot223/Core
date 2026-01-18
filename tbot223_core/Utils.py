# external Modules
from pathlib import Path
from typing import Optional, Union, List, Any, Dict, Callable
import time
import hashlib, secrets
import logging
import struct
from multiprocessing import RLock, shared_memory, Lock
import pickle, json

# internal Modules
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker
from tbot223_core import LogSys

class Utils:
    """
    Utility class providing various helper functions.

    Methods:
        - str_to_path(path_str) -> Result
            Convert a string to a Path object.
        
        - encrypt(data, algorithm) -> Result
            Encrypt a string using the specified algorithm.

        - pbkdf2_hmac(password, algorithm, iterations, salt_size) -> Result
            Generate a PBKDF2 HMAC hash of the given password.

        - verify_pbkdf2_hmac(password, salt_hex, hash_hex, iterations, algorithm) -> Result
            Verify a PBKDF2 HMAC hash of the given password.

        - insert_at_intervals(data, interval, insert, at_start) -> Result
            Insert a specified element into a list or string at regular intervals.

        - find_keys_by_value(dict_obj, threshold, comparison, nested) -> Result
            Find keys in a dictionary based on value comparisons.
    """
    
    def __init__(self, is_logging_enabled: bool=False,
                 base_dir: Union[str, Path]=None,
                 logger_manager_instance: Optional[LogSys.LoggerManager]=None, logger: Optional[logging.Logger]=None, 
                 log_instance: Optional[LogSys.Log]=None):
        """
        Initialize Utils class.
        """
        # Initialize Paths
        self._BASE_DIR = Path(base_dir or Path.cwd())

        # Initialize Flags
        object.__setattr__(self, '__is_logging_enabled__', is_logging_enabled)

        # Initialize Classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self._logger = None
        if self.__is_logging_enabled__:
            self._logger_manager = logger_manager_instance or LogSys.LoggerManager(base_dir=self._BASE_DIR / "logs", second_log_dir="utils")
            self._logger_manager.make_logger("UtilsLogger")
            self._logger = logger or self._logger_manager.get_logger("UtilsLogger").data
        self.log = log_instance or LogSys.Log(logger=self._logger)

        if self.__is_logging_enabled__:
            self.log.log_message("INFO", "Utils initialized.")

    # Internal Methods
    def _check_pbkdf2_params(self, password: str, algorithm: str, iterations: int, salt_size: int = 32) -> None:
        """
        Check parameters for PBKDF2 HMAC functions.

        Args:
            - password : The password string.
            - algorithm : The hashing algorithm to use.
            - iterations : Number of iterations.
            - salt_size : Size of the salt in bytes (default: 32).

        Raises:
            ValueError: If any parameter is invalid.
        
        Example:
            >>> I'm Not recommending to call this method directly, It's for internal use.
            >>> utils = Utils()
            >>> utils._check_pdkdf2_params("my_password", "sha256", 100000, 32)
            >>> # No exception raised for valid parameters.
        """
        if not isinstance(password, str):
            raise ValueError("password must be a string")
        if algorithm not in ['sha1', 'sha256', 'sha512']:
            raise ValueError("Unsupported algorithm. Supported algorithms: 'sha1', 'sha256', 'sha512'")
        if not isinstance(iterations, int) or iterations <= 0:
            raise ValueError("iterations must be a positive integer")
        if not isinstance(salt_size, int) or salt_size <= 0:
            raise ValueError("salt_size must be a positive integer")
        
    def _lookup_dict(self, dict_obj: Dict, threshold: Union[int, float, str, bool], comparison_func: Callable, comparison_type: str, nested: bool, nest_mark: str = "") -> List:
        """
        Helper method to recursively look up keys in a dictionary based on a comparison function.

        Args:
            dict_obj : The dictionary to search.
            threshold : The value to compare against.
            comparison_func : A callable that takes a value and returns True if it meets the condition.
            comparison_type : The type of comparison being performed.
            nested : If True, search within nested dictionaries.

        Returns:
            A list of keys that meet the comparison criteria.

        Example:
            >>> # I'm not recommending to call this method directly, it's for internal use.
            >>> my_dict = {'a': 10, 'b': 20, 'c': 30}
            >>> found_keys = app_core._lookup_dict(my_dict, threshold=20, comparison_func=lambda x: x > 20, comparison_type='gt', nested=False)
            >>> print(found_keys)  # Output: ['c']
        """
        found_keys = []
        for key, value in dict_obj.items():
            if isinstance(value, (str, bool)) != isinstance(threshold, (str, bool)) and comparison_type in ['eq', 'ne']:
                continue
            if isinstance(value, (tuple, list)):
                continue
            if comparison_func(value):
                found_keys.append(f"{nest_mark}{key}")
                if self.__is_logging_enabled__:
                    self.log.log_message("DEBUG", f"Key '{nest_mark}{key}' matches the condition.")
            if nested and isinstance(value, dict):
                if self.__is_logging_enabled__:
                    self.log.log_message("DEBUG", f"Searching nested dictionary at key '{key}'.")
                found_keys.extend(self._lookup_dict(value, threshold, comparison_func, comparison_type, nested, f"{nest_mark}{key}."))
        return found_keys

    # external Methods
    def str_to_path(self, path_str: str) -> Path:
        """
        Convert a string to a Path object.

        Args:
            - path_str : The string representation of the path.
            
        Returns:
            Result: A Result object containing the Path object.
        
        Example:
            >>> result = utils.str_to_path("/home/user/documents")
            >>> if result.success:
            >>>     path = result.data # Path object
            >>>     print(path.exists())
            >>> else:
            >>>     print(result.error)
        """
        try:
            if not isinstance(path_str, str):
                return Result(True, None, None, path_str)

            return Result(True, None, None, Path(path_str))
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def encrypt(self, data: str, algorithm: str='sha256') -> Result:
        """
        Encrypt a string using the specified algorithm.
        Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'

        Args:
            - data : The string to encrypt.
            - algorithm : The hashing algorithm to use. Defaults to 'sha256'

        Returns:
            Result: A Result object containing the encrypted string in hexadecimal format.

        Example:
            >>> result = utils.encrypt("my_secret_data", algorithm='sha256')
            >>> if result.success:
            >>>     encrypted_data = result.data
            >>>     print(encrypted_data)
            >>> else:
            >>>     print(result.error)
        """
        try:
            if not isinstance(data, str):
                raise ValueError("data must be a string")
            if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
                raise ValueError("Unsupported algorithm. Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'")

            hash_func = getattr(hashlib, algorithm)()
            hash_func.update(data.encode('utf-8'))
            encrypted_data = hash_func.hexdigest()

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Data encrypted using {algorithm}.")
            return Result(True, None, None, encrypted_data)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Encryption failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def pbkdf2_hmac(self, password: str, algorithm: str, iterations: int, salt_size: int) -> Result:
        """
        Generate a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns a dict containing the salt (hex), hash (hex), iterations, and algorithm used.

        Args:
            - password : The password string.
            - algorithm : The hashing algorithm to use.
            - iterations : Number of iterations.
            - salt_size : Size of the salt in bytes.

        Returns:
            Result: A Result object containing a dict with the following keys:
        
        Example:
            >>> result = utils.pbkdf2_hmac("my_password", "sha256", 100000, 32)
            >>> if result.success:
            >>>     hash_info = result.data
            >>>     print(hash_info)
            >>> else:
            >>>     print(result.error)
        """
        try:
            self._check_pbkdf2_params(password, algorithm, iterations, salt_size)
            
            salt = secrets.token_bytes(salt_size)
            hash_bytes = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)

            salt_hex = salt.hex()
            hash_hex = hash_bytes.hex()
            result = {
                "salt_hex": salt_hex,
                "hash_hex": hash_hex,
                "iterations": iterations,
                "algorithm": algorithm
            }

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"PBKDF2 HMAC hash generated using {algorithm} with {iterations} iterations.")
            return Result(True, None, None, result)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"PBKDF2 HMAC hash generation failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def verify_pbkdf2_hmac(self, password: str, salt_hex: str, hash_hex: str, iterations: int, algorithm: str) -> Result:
        """
        Verify a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns True if the password matches the hash, False otherwise.

        Args:
            - password : The password string to verify.
            - salt_hex : The salt in hexadecimal format.
            - hash_hex : The hash in hexadecimal format.
            - iterations : Number of iterations.
            - algorithm : The hashing algorithm to use.

        Returns:
            Result: A Result object containing a boolean indicating whether the password matches the hash.

        Example:
            >>> hash_info = {
            >>>     "salt_hex": "a1b2c3d4e5f6...",
            >>>     "hash_hex": "abcdef123456...",
            >>>     "iterations": 100000,
            >>>     "algorithm": "sha256"
            >>> }
            >>> result = utils.verify_pbkdf2_hmac("my_password", hash_info["salt_hex"], hash_info["hash_hex"], hash_info["iterations"], hash_info["algorithm"])
            >>> if result.success:
            >>>     is_valid = result.data
            >>>     print(is_valid)  # True or False
            >>> else:
            >>>     print(result.error)
        """
        try:
            self._check_pbkdf2_params(password, algorithm, iterations)
            if not isinstance(salt_hex, str) or not isinstance(hash_hex, str):
                raise ValueError("salt_hex and hash_hex must be strings")
            
            salt = bytes.fromhex(salt_hex)
            hash_bytes = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)
            computed_hash_hex = hash_bytes.hex()

            is_valid = computed_hash_hex == hash_hex
            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"PBKDF2 HMAC hash verification using {algorithm} with {iterations} iterations. Result: {is_valid}")
            return Result(True, None, None, is_valid)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"PBKDF2 HMAC hash verification failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def insert_at_intervals(self, data: Union[List, str], interval: int, insert: Any, at_start: bool=True) -> Result:
        """
        Insert a specified element into a list or string at regular intervals.

        Args:
            - data (list or str): The original list or string where elements will be inserted.
            - interval (int): The interval at which to insert the element. (must be a positive integer)
            - insert (Any): The element to insert into the list or string. (if data is a string, using object like callable is not recommended as it will be converted to string)
            - at_start (bool, optional): If True, insertion starts at the beginning (index 0). If False, insertion starts after the first interval. Defaults to True.

        Returns:
            Result: A Result object containing the modified list or string.

        Example:
            >>> utils = Utils()
            >>> data_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            >>> result = utils.insert_at_intervals(data_list, 3, 'X', at_start=True)
            >>> if result.success:
            >>>    print(result.data)  # Output: ['X', 1, 2, 3, 'X', 4, 5, 6, 'X', 7, 8, 9]
            >>> else:
            >>>    print(result.error)
        """
        try:
            if not isinstance(data, (list, str)):
                raise ValueError("data must be a list or string")
            if not isinstance(interval, int) or interval <= 0:
                raise ValueError("interval must be a positive integer")
            if not isinstance(at_start, bool):
                raise ValueError("at_start must be a boolean value")
        
            original_type_is_str = False
            if isinstance(data, str):
                original_type_is_str = True
                data = list(data)

            # Build new list by inserting at intervals (iterate in reverse to avoid index shifting issues)
            result_data = list(data)
            start_index = 0 if at_start else interval
            insert_count = 0
            
            # Calculate positions from the end to maintain correct indices
            positions_to_insert = list(range(start_index, len(result_data) + insert_count * (interval + 1), interval + 1))
            
            # Insert in reverse order to avoid index shifting
            for pos in reversed(positions_to_insert):
                if pos <= len(result_data):
                    result_data.insert(pos, insert)
                    insert_count += 1

            if original_type_is_str:
                result_data = ''.join(map(str, result_data))
            return Result(True, None, None, result_data)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
    
    def find_keys_by_value(self, dict_obj: Dict, threshold: Union[int, float, str, bool],  comparison: str='eq', nested: bool=False) -> Result:
        """
        Find keys in dict_obj where their values meet the threshold based on the comparison operator.

        [bool, str] - [int, float] comparisons are only supported for 'eq' and 'ne'.

        Args:
            dict_obj : The dictionary to search.
            threshold : The value to compare against.
            comparison : The comparison operator as a string. Default is 'eq' (equal).
            nested : If True, search within nested dictionaries.

        Returns:
            A list of keys that meet the comparison criteria.

        Example:
            >>> my_dict = {'a': 10, 'b': 20, 'c': 30}
            >>> result = app_core.find_keys_by_value(my_dict, threshold=20, comparison='gt', nested=False)
            >>> print(result.data)  # Output: ['c']

        Supported comparison operators:
        - 'eq': equal to
        - 'ne': not equal to
        - 'lt': less than
        - 'le': less than or equal to
        - 'gt': greater than
        - 'ge': greater than or equal to
        """
        comparison_operators = {
            'eq': lambda x: x == threshold,
            'ne': lambda x: x != threshold,
            'lt': lambda x: x < threshold,
            'le': lambda x: x <= threshold,
            'gt': lambda x: x > threshold,
            'ge': lambda x: x >= threshold,
        }

        try:
            if comparison not in comparison_operators:
                raise ValueError(f"Unsupported comparison operator: {comparison}")
            if isinstance(dict_obj, dict) is False:
                raise ValueError("Input data must be a dictionary")
            if isinstance(threshold, (str, bool, int, float)) is False:
                raise ValueError("Threshold must be of type str, bool, int, or float")
            
            comparison_func = comparison_operators[comparison]
            found_keys = self._lookup_dict(dict_obj, threshold, comparison_func, comparison, nested)

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"find_keys_by_value found {len(found_keys)} keys matching criteria.")
            return Result(True, None, None, found_keys)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Error in find_keys_by_value: {str(e)}")
            return self._exception_tracker.get_exception_return(e)
        
class DecoratorUtils:
    """
    This class provides utility decorators for various purposes.

    Methods:
        - count_runtime() -> function
            Decorator to measure and print the execution time of a function.
    """

    
    def __init__(self):
        self._exception_tracker = ExceptionTracker()

    # Internal Methods

    # external Methods
    @staticmethod
    def count_runtime():
        """
        Decorator to measure and print the execution time of a function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                run_time = end_time - start_time
                print(f"This ran for {run_time:.4f} seconds.")
                return result
            return wrapper
        return decorator
    
    def make_decorator(self, func):
        """
        Decorator to handle exceptions and return a Result object.
        
        Args:
            - func : The function to decorate.
            
        Returns:
            A wrapper function that returns a Result object on exception.
            
        Example:
            >>> def my_function(x):
            >>>     return 10 / x
            >>> decorated_function = DecoratorUtils().make_decorator(my_function)
            >>> @decorated_function
            >>> def safe_function(x):
            >>>     return 10 / x
            >>> result = safe_function(0)

        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return self._exception_tracker.get_exception_return(e)
        return wrapper
    
class GlobalVars:
    """
    This class manages global variables in a controlled manner.

    Recommended usage:
    - Beginners use explicit methods.
    - Advanced users can use attribute access or call syntax.

    Methods:
        - set(key: str, value: object, overwrite) -> Result
            Set a global variable.
        
        - get(key: str) -> Result
            Get a global variable.

        - delete(key: str) -> Result
            Delete a global variable.

        - clear() -> Result
            Clear all global variables.

        - list_vars() -> Result
            List all global variables.

        - exists(key: str) -> Result
            Check if a global variable exists.

        # internal Methods
        - __getattr__(name)
            Get a global variable by attribute access.

        - __setattr__(name, value)
            Set a global variable by attribute access.  

        - __call__(key: str, value: Optional[object], overwrite: bool) -> Result 
            Get or set a global variable using call syntax.

        - __enter__() -> GlobalVars
            Enter the runtime context related to this object. ( mutiprocess.RLock acquisition )

        - __exit__(exc_type, exc_value, traceback) -> None
            Exit the runtime context related to this object. ( mutiprocess.RLock release )

        # shared memory Methods

        - shm_cache_management(name: Optional[str], shm: Optional[shared_memory.SharedMemory]) -> Result
            Internal method to manage shared memory cache.

        - shm_gen(name: str, size: int) -> Result
            Generate a shared memory object for global variables.

        - shm_connect(name: str) -> Result
            Connect to an existing shared memory object for global variables.

        - shm_get(name: str) -> Result
            Get the shared memory object by name.

        - shm_close(name: str, close_only: bool = False) -> Result
            Close a shared memory object for global variables.
        
        - shm_update(name: str) -> Result
            Update the current object's variables from the shared memory object.

        - shm_sync(name: str) -> Result
            Synchronize the current object's variables to the shared memory object.

        - lock() -> RLock
            Get the RLock object for synchronizing access to global variables.

    Example:
        >>> globals = GlobalVars()
        >>> globals.set("api_key", "12345", overwrite=True)
        >>> result = globals.get("api_key")
        >>> if result.success:
        >>>     print(result.data)  # Output: 12345
        >>> else:
        >>>     print(result.error)

        >>> # or using attribute access:

        >>> globals.api_key = "12345"
        >>> print(globals.api_key)  # Output: 12345
        
        >>> # or using call syntax:

        >>> globals("api_key", "12345", overwrite=True)
        >>> print(globals("api_key").data)  # Output: 12345
    
    Security:
    - The shared-memory methods ('shm_sync', 'shm_update', etc.) support two 
        serialization formats: 'pickle' (default) and 'json'.
    - PICKLE: Unpickling untrusted data can execute arbitrary code. Use pickle 
        serialization only between trusted processes.
    - JSON: Safe for untrusted processes but has limitations (cannot serialize 
        all Python objects like custom classes, functions, etc.).
    - To use JSON serialization for safer inter-process communication:
        >>> gv.shm_sync("my_shm", serialize_format="json")
        >>> gv.shm_update("my_shm", serialize_format="json")
    - Always validate and verify data integrity when using shared memory with
        untrusted processes, regardless of serialization format.

    """

    def __init__(self, is_logging_enabled: bool=False, base_dir: Union[str, Path]=None,
                 shared_memory_cache_max_size: int=5,
                 logger_manager_instance: Optional[LogSys.LoggerManager]=None, logger: Optional[logging.Logger]=None, 
                 log_instance: Optional[LogSys.Log]=None):
        
        # Set initialization flag to bypass __setattr__ during __init__
        object.__setattr__(self, '__initializing__', True)
        object.__setattr__(self, '__vars__', {})
        object.__setattr__(self, '__lock__', RLock())
        
        # Initialize Paths
        self._BASE_DIR = Path(base_dir) if base_dir is not None else Path.cwd()

        # Initialize Flags
        self.__is_logging_enabled__ = is_logging_enabled

        # Initialize Classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self._logger = None
        if self.__is_logging_enabled__:
            self._logger_manager = logger_manager_instance or LogSys.LoggerManager(base_dir=self._BASE_DIR / "logs", second_log_dir="global_vars")
            self._logger_manager.make_logger("GlobalVarsLogger")
            self._logger = logger or self._logger_manager.get_logger("GlobalVarsLogger").data
        self.log = log_instance or LogSys.Log(logger=self._logger)

        # Shared Memory Attributes
        self.__shm_name__ = set()
        self.__shm_cache__ = {}
        self.__shm_cache_max_size__ = shared_memory_cache_max_size

        self.SERIALIZERS = {
            "pickle": (
                    lambda obj: pickle.dumps(obj), 
                    lambda byte_data: pickle.loads(byte_data)
            ),
            "json": (
                    lambda obj: json.dumps(obj).encode('utf-8'), 
                    lambda byte_data: json.loads(byte_data.decode('utf-8'))
            )
        }

        # Initialization complete
        object.__setattr__(self, '__initializing__', False)
        
    def set(self, key: str, value: object, overwrite: bool=False) -> Result:
        """
        Set a global variable.
        
        Args:
            - key : The name of the global variable.
            - value : The value to set.
            - overwrite : If True, overwrite existing variable. Defaults to False.

        Returns:
            Result: A Result object indicating success or failure.
        
        Example:
            >>> globals = GlobalVars()
            >>> result = globals.set("api_key", "12345", overwrite=True)
            >>> if result.success:
            >>>     print(result.data)  # Output: Global variable 'api_key' set.
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                # inline existence check to avoid extra lock/log overhead from exists()
                if key in self.__vars__ and not overwrite:
                    raise KeyError(f"Global variable '{key}' already exists.")
                if key is None or not isinstance(key, str) or key.strip() == "":
                    raise ValueError("key must be a non-empty string.")

                self.__vars__[key] = value
                if self.__is_logging_enabled__:
                    self.log.log_message("INFO", f"Global variable '{key}' set.")
                return Result(True, None, None, f"Global variable '{key}' set.")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to set global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def get(self, key: str) -> Result:
        """
        Get a global variable.

        Args:
            - key : The name of the global variable.

        Returns:
            Result: A Result object containing the value of the global variable.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.get("api_key")
            >>> if result.success:
            >>>     print(result.data)  # Output: 12345
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                if key not in self.__vars__:
                    raise KeyError(f"Global variable '{key}' does not exist.")

                if self.__is_logging_enabled__:
                    self.log.log_message("INFO", f"Global variable '{key}' accessed.")
                return Result(True, None, None, self.__vars__[key])
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to get global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def delete(self, key: str) -> Result:
        """
        Delete a global variable.

        Args:
            - key : The name of the global variable.
        
        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.delete("api_key")
            >>> if result.success and not globals.exists("api_key").data:
            >>>     print("api_key deleted successfully.")
            >>> else:
            >>>     print("Failed to delete api_key.")
        """
        try:
            with self.__lock__:
                if key not in self.__vars__:
                    raise KeyError(f"Global variable '{key}' does not exist.")

                del self.__vars__[key]
                if self.__is_logging_enabled__:
                    self.log.log_message("INFO", f"Global variable '{key}' deleted.")
                return Result(True, None, None, f"Global variable '{key}' deleted.")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to delete global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def clear(self) -> Result:
        """
        Clear all global variables.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> globals.set("user_id", "user_01", overwrite=True)
            >>> result = globals.clear()
            >>> if result.success and len(globals.list_vars().data) == 0:
            >>>     print("All global variables cleared.")
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                for name in list(self.__vars__.keys()):
                    del self.__vars__[name]

                if self.__is_logging_enabled__:
                    self.log.log_message("INFO", "All global variables cleared.")
                return Result(True, None, None, "All global variables cleared.")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to clear global variables: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def list_vars(self) -> Result:
        """
        List all global variables.

        Returns:
            Result: A Result object containing a list of global variable names.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> globals.set("user_id", "user_01", overwrite=True)
            >>> result = globals.list_vars()
            >>> if result.success:
            >>>     print(result.data)  # Output: ['api_key', 'user_id']
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                if self.__is_logging_enabled__:
                    self.log.log_message("INFO", "Listing all global variables.")
                return Result(True, None, None, list(self.__vars__.keys()))
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to list global variables: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def exists(self, key: str) -> Result:
        """
        Check if a global variable exists.

        Args:
            - key : The name of the global variable.

        Returns:
            Result: A Result object containing a boolean indicating existence.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.exists("api_key")
            >>> if result.success:
            >>>     print(result.data)  # Output: True
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                exists = key in self.__vars__
                if self.__is_logging_enabled__:
                    self.log.log_message("INFO", f"Checked existence of global variable '{key}': {exists}")
                return Result(True, None, None, exists)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to check existence of global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def __getattr__(self, name):
        """
        Get a global variable by attribute access.

        Args:
            - name : The name of the global variable.

        Returns:
            The value of the global variable.

        Example:
            >>> globals = GlobalVars()
            >>> globals.api_key = "12345"
            >>> print(globals.api_key)  # Output: 12345 ( this part uses __getattr__ )
        """
        try:
            with object.__getattribute__(self, '__lock__'):
                if name not in self.__vars__:
                    raise KeyError(f"Global variable '{name}' does not exist.")
                return self.__vars__[name]
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def __setattr__(self, name, value):
        """
        Set a global variable by attribute access.

        Args:
            - name : The name of the global variable.
            - value : The value to set.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.api_key = "12345" ( this part uses __setattr__ )
            >>> print(globals.api_key)  # Output: 12345
        """
        # During initialization, use normal attribute setting
        try:
            if object.__getattribute__(self, '__initializing__'):
                object.__setattr__(self, name, value)
                return
        except AttributeError:
            # __initializing__ not set yet, must be during early init
            object.__setattr__(self, name, value)
            return
        
        # After initialization, store in __vars__ dict
        try:
            with object.__getattribute__(self, '__lock__'):
                if name is None or not isinstance(name, str) or name.strip() == "":
                    raise ValueError("name must be a non-empty string.")
                
                vars_dict = object.__getattribute__(self, '__vars__')
                vars_dict[name] = value
        except Exception as e:
            exception_tracker = object.__getattribute__(self, '_exception_tracker')
            return exception_tracker.get_exception_return(e)
        
    def __call__(self, key: str, value: Optional[object]=None, overwrite: bool=False) -> Result:
        """
        Get or set a global variable using call syntax.
        If value is provided, set the variable; otherwise, get it.

        Args:
            - key : The name of the global variable.
            - value : The value to set (optional).
            - overwrite : If True, overwrite existing variable when setting. Defaults to False.

        Returns:
            Result: A Result object containing the value when getting, or indicating success/failure when setting

        Example:
            >>> globals = GlobalVars()
            >>> globals("api_key", "12345", overwrite=True)  # Set api_key
            >>> result = globals("api_key")  # Get api_key
            >>> if result.success:
            >>>     print(result.data)  # Output: 12345
            >>> else:
            >>>     print(result.error)
        """
        try:
            if value is not None:
                return self.set(key, value, overwrite)
            else:
                return self.get(key)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def shm_cache_management(self, name: Optional[str], shm: Optional[shared_memory.SharedMemory]) -> Result:
        """
        Internal method to manage shared memory cache.

        Security: This method manages shared memory cache; shared-memory data
        may be serialized by other methods using pickle or json format.
        Use json format (serialize_format="json") for untrusted processes.

        Args:
            - name: The name of the shared memory object.
            - shm: The shared memory object.
            if name and shm are provided, it adds/updates the cache.
            if both are None, it clears the cache.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> shm = shared_memory.SharedMemory(name="my_shm")
            >>> gv.__shm_cache_management__("my_shm", shm)
            >>> # Manages the shared memory cache for "my_shm".
            >>>
            >>> for i in range(6):
            >>>     shm = shared_memory.SharedMemory(name=f"shm_{i}")
            >>>     gv.__shm_cache_management__(f"shm_{i}", shm)
            >>> # The cache will only keep the 5 most recent shared memory objects.
        """
        try:
            if name is not None and not isinstance(name, str):
                raise ValueError("name must be a string or None")
            if shm is not None and not isinstance(shm, shared_memory.SharedMemory):
                raise ValueError("shm must be a shared_memory.SharedMemory object or None")
            with self.__lock__:
                if len(self.__shm_cache__) >= self.__shm_cache_max_size__:
                    oldest_key = next(iter(self.__shm_cache__))
                    self.__shm_cache__[oldest_key].close()
                    del self.__shm_cache__[oldest_key]
                    if self.__is_logging_enabled__:
                        self.log.log_message("INFO", f"Shared memory cache for '{oldest_key}' removed due to cache size limit.")

                if name not in self.__shm_cache__ and shm is not None:
                    self.__shm_cache__[name] = shm
                    if self.__is_logging_enabled__:
                        self.log.log_message("INFO", f"Shared memory cache for '{name}' created.")
                elif name in self.__shm_cache__ and shm is not None:
                    self.__shm_cache__[name] = shm
                    if self.__is_logging_enabled__:
                        self.log.log_message("INFO", f"Shared memory cache for '{name}' updated.")
                elif name is None and shm is None:
                    self.__shm_cache__.clear()
                    if self.__is_logging_enabled__:
                        self.log.log_message("INFO", "All shared memory caches cleared.")
                else:
                    shm_obj = self.__shm_cache__.get(name)
                    self.__shm_cache__.pop(name, None)
                    self.__shm_cache__[name] = shm_obj
                    if self.__is_logging_enabled__:
                        self.log.log_message("INFO", f"Shared memory cache for '{name}' accessed.")

            return Result(True, None, None, "success to manage shared memory cache")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to manage shared memory cache: {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_gen(self, name: str=None, size: int=1024, create_lock: bool=True) -> Result:
        """
        Generate a shared memory object for inter-process communication.
        Recommended to use a Lock for safe access across processes.

        Security: The shared memory object may be used to store data serialized
        with pickle (default) or json. For untrusted processes, use json format:
        >>> gv.shm_sync("name", serialize_format="json")

        Args:
            - name: The name of the shared memory object.
            - size: The size of the shared memory object in bytes.
            - create_lock: If True, create a multiprocessing.Lock for inter-process synchronization.

        Returns:
            Result: A Result object.
            - If create_lock is False: data contains a success message.
            - If create_lock is True: data contains the multiprocessing.Lock object.
              (This lock must be passed to child processes before fork/spawn for synchronization)
        
        Example:
            >>> # Without lock (default)
            >>> gv.shm_gen("my_shm", size=4096)
            >>> 
            >>> # With lock for inter-process synchronization
            >>> result = gv.shm_gen("my_shm", size=4096, create_lock=True)
            >>> shm_lock = result.data  # Pass this to child processes
            >>> 
            >>> # In child process, use the lock:
            >>> with shm_lock:
            >>>     gv.shm_update("my_shm")
            >>>     # ... modify ...
            >>>     gv.shm_sync("my_shm")
        """
        try:
            if name is None or not isinstance(name, str) or name.strip() == "":
                raise ValueError("name must be a non-empty string.")
            if not isinstance(size, int) or size <= 0:
                raise ValueError("size must be a positive integer.")
            
            try:
                shm = shared_memory.SharedMemory(create=True, size=size, name=name)
            except FileExistsError:
                shm = shared_memory.SharedMemory(name=name)
            self.__shm_name__.add(name)
            self.shm_cache_management(name, shm)  # Keep reference to prevent GC
            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Shared memory object '{shm.name}' created.")
            
            if create_lock:
                lock = Lock()
                return Result(True, None, None, lock)
            return Result(True, None, None, "success to create shared memory object")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to create shared memory object: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def shm_connect(self, name: str) -> Result:
        """
        Connect to an existing shared memory object (for child processes).
        Unlike shm_gen, this method only connects to existing shared memory
        and does not create new one or Lock.

        Security: Connected shared memory may contain pickle or json serialized data.
        Ensure you use the same serialization format when calling shm_sync/shm_update.

        Args:
            - name: The name of the existing shared memory object.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> # In main process:
            >>> gv_main = GlobalVars()
            >>> result = gv_main.shm_gen("my_shm", size=4096, create_lock=True)
            >>> shm_lock = result.data
            >>> 
            >>> # In child process:
            >>> gv_child = GlobalVars()
            >>> gv_child.shm_connect("my_shm")  # Connect to existing shm
            >>> with shm_lock:
            >>>     gv_child.shm_update("my_shm")
            >>>     # ... modify ...
            >>>     gv_child.shm_sync("my_shm")
        """
        try:
            res = self.shm_get(name)
            if not res.success:
                return res

            if name not in self.__shm_name__:
                self.__shm_name__.add(name)

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Connected to shared memory object '{name}'.")
            return Result(True, None, None, f"Connected to shared memory object '{name}'.")
        except FileNotFoundError:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Shared memory object '{name}' does not exist.")
            return Result(False, "FileNotFoundError", f"Shared memory object '{name}' does not exist.", None)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to connect to shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_get(self, name: str) -> Result:
        """
        Get an existing shared memory object by name.

        Security: Retrieved shared memory may contain pickle or json serialized data.
        Use json format for safer inter-process communication with untrusted sources.

        Args:
            - name: The name of the shared memory object.

        Returns:
            shared_memory.SharedMemory: The existing shared memory object.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> shm = gv.shm_get("my_shm").data
            >>> print(shm.name)  # Output: my_shm
        """
        try:
            if name not in self.__shm_cache__:
                if self.__is_logging_enabled__:
                    self.log.log_message("WARNING", f"Shared memory object '{name}' not found in cache.")
                shm = shared_memory.SharedMemory(name=name)
                self.shm_cache_management(name, shm)
                if self.__is_logging_enabled__:
                    self.log.log_message("INFO", f"Shared memory object '{name}' created and added to cache.")
                return Result(True, None, None, shm)
            shm = self.__shm_cache__[name]
            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Shared memory object '{name}' retrieved from cache.")
            return Result(True, None, None, shm)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to retrieve shared memory object '{name}' from cache: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def shm_sync(self, name: str, serialize_format: str="pickle") -> Result:
        """
        Synchronize the current object's variables to the shared memory object.

        Security: This method supports 'pickle' (default) and 'json' serialization.
        - pickle: Fast but dangerous with untrusted data (arbitrary code execution)
        - json: Safe but limited (cannot serialize custom classes, functions, etc.)
        For untrusted processes, always use serialize_format="json".

        Args:
            - name: The name of the shared memory object.
            - serialize_format: The serialization format to use. Default is "pickle". ("pickle" or "json")

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> gv.some_variable = 42
            >>> gv.shm_sync("my_shm")
            >>> # In another process:
            >>> gv.shm_update("my_shm")
            >>> print(gv.some_variable)  # Output: 42
        """
        try:
            if serialize_format not in self.SERIALIZERS:
                raise ValueError(f"Unsupported serialization format: {serialize_format}")
            
            byte_dict = self.SERIALIZERS[serialize_format][0](self.__vars__)
                
            data_len = len(byte_dict)
            header_size = 8 # bytes to store length of data

            if name not in self.__shm_name__:
                raise ValueError("Shared memory name does not match the created one.")
            if name not in self.__shm_cache__:
                shm = shared_memory.SharedMemory(name=name)
                self.shm_cache_management(name, shm)
            else:
                shm = self.__shm_cache__[name]

            if data_len + header_size > shm.size:
                raise MemoryError(f"Serialized data size ({data_len + header_size} bytes) exceeds shared memory size ({shm.size} bytes).")
            
            shm.buf[:header_size] = struct.pack('Q', data_len)
            shm.buf[header_size:header_size+data_len] = byte_dict

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Shared memory object '{name}' synchronized.")
            return Result(True, None, None, "success to synchronize shared memory object")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to synchronize shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def shm_update(self, name: str, serialize_format: str="pickle") -> Result:
        """
        Update the current object's variables from the shared memory object.

        Security: This method supports 'pickle' and 'json' deserialization.
        - pickle: Dangerous with untrusted data (can execute arbitrary code)
        - json: Safe for untrusted data but has serialization limitations
        Always use the same format that was used in shm_sync().
        
        Args:
            - name: The name of the shared memory object.
            - serialize_format: The serialization format to use. Default is "pickle". ("pickle" or "json")

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> gv.some_variable = 42
            >>> gv.shm_sync("my_shm")
            >>> # In another process:
            >>> gv.shm_update("my_shm", serialize_format="pickle")
            >>> print(gv.some_variable)  # Output: 42
        """
        try:
            if serialize_format not in self.SERIALIZERS:
                raise ValueError(f"Unsupported serialization format: {serialize_format}")
            
            shm = self.shm_get(name).data
            header_size = 8 # bytes to store length of data

            packed_len = bytes(shm.buf[:header_size])
            (data_len,) = struct.unpack('Q', packed_len)

            if data_len == 0:
                if self.__is_logging_enabled__:
                    self.log.log_message("WARNING", f"No data found in shared memory object '{name}'.")
                return Result(True, None, None, "no data to update from shared memory object")
            
            byte_dict = bytes(shm.buf[header_size:header_size+data_len])

            try:
                obj_dict = self.SERIALIZERS[serialize_format][1](byte_dict)
            except Exception as e:
                raise ValueError(f"Unpickling error. Read {data_len} bytes from shared memory but failed to unpickle: {e}")

            with self.__lock__:
                self.__vars__.update(obj_dict)

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Shared memory object '{name}' updated.")
            return Result(True, None, None, "success to update from shared memory object")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to update from shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def shm_close(self, name: str, close_only: bool = False) -> Result:
        """
        Close and unlink the shared memory object.

        Args:
            - name: The name of the shared memory object.
            - close_only: If True, only close the shared memory without unlinking it.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> gv.shm_close("my_shm")
        """
        try:
            if name not in self.__shm_name__:
                raise ValueError("Shared memory name does not match the created one.")
            shm = self.shm_get(name).data
            shm.close()
            if not close_only:
                shm.unlink()
                self.__shm_name__.discard(name)
            self.__shm_cache__.pop(name, None)

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Shared memory object '{name}' closed and unlinked.")
            return Result(True, None, None, "success to close shared memory object")
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Failed to close shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def lock(self) -> RLock: # type: ignore
        """
        Get the RLock object for synchronizing access to global variables.

        Args:
            None

        Returns:
            multiprocessing.RLock: The RLock object.
            (For the user's convenience, this function does not specifically use the Result pattern.)

        Example:
            >>> gv = GlobalVars()
            >>> with gv.lock():
            >>>     gv.set("counter", gv.get("counter").data + 1, overwrite=True)
            >>>     # Critical section to safely modify 'counter'
        """
        return self.__lock__
    
    def __enter__(self):
        self.__lock__.acquire()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.__lock__.release()