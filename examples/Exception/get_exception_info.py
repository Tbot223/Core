# avoid `Exception` name conflict
from tbot223_core import Exception as Exc

if __name__ == "__main__":
    # Initialize ExceptionTracker
    tracker = Exc.ExceptionTracker()

    # Test getting exception information
    try:
        1 / 0
    except Exception as e:
        exc_info = tracker.get_exception_info(e)
        print("Exception Info:", exc_info)

    print("\n\n ------- masked ------- \n\n")
    # Test getting exception information with masking
    try:
        lst = [1, 2, 3]
        print(lst[5])
    except Exception as e:
        exc_info_masked = tracker.get_exception_info(e, masking=True)
        print("Masked Exception Info:", exc_info_masked)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")