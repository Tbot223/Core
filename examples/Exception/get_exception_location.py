# avoid `Exception` name conflict
from tbot223_core import Exception as Exc

if __name__ == "__main__":
    # Initialize ExceptionTracker
    tracker = Exc.ExceptionTracker()

    # Test getting exception location
    try:
        1 / 0
    except Exception as e:
        location_result = tracker.get_exception_location(e)
        print("Exception Location:", location_result.data)

    print("\n -------------- TEST COMPLETE -------------- \n")