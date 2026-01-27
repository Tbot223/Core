from pathlib import Path
from tbot223_core.AppCore import ResultWrapper

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

# Example usage of ResultWrapper 
def example_function(x: int, y: int) -> int: # not decorated
    return x + y

@ResultWrapper()
def decorated_function(x: int, y: int) -> ResultWrapper: # decorated
    return x + y

if __name__ == "__main__":
    a, b = 5, 10

    # Using the undecorated function
    try:
        result = example_function(a, b)
        print(f"Undecorated function result: {result}")
    except Exception as e:
        print(f"Undecorated function raised an exception: {e}")

    # Using the decorated function
    wrapped_result = decorated_function(a, b)
    if wrapped_result.success:
        print(f"Decorated function result: {wrapped_result.data}")
    else:
        print(f"Decorated function raised an exception: {wrapped_result.error_message}")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")