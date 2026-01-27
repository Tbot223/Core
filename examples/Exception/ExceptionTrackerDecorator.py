from tbot223_core import Exception

# Example usage of ExceptionTrackerDecorator
# This function will be decorated to track exceptions. so it will be safety executed.
@Exception.ExceptionTrackerDecorator()
def risky_division(a, b):
    return a / b

if __name__ == "__main__":
    # Test the decorated function ( args )
    result = risky_division(10, 0)
    print("error:", result.error)
    print("Params:", result.data["input_context"]["params"], end="\n\n")

    # Test the decorated function ( kwargs )
    result = risky_division(a=10, b=0)
    print("error:", result.error)
    print("Result:", result.data["input_context"]["params"], end="\n\n")

    # Test the decorated function ( mixed )
    result = risky_division(10, b=0)
    print("error:", result.error)
    print("Params:", result.data["input_context"]["params"], end="\n\n")

    # Test the decorated function ( no error )
    result = risky_division(10, 2)
    print(result) # it should be not Result object, just return value

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")