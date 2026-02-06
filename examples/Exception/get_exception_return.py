# avoid `Exception` name conflict
from tbot223_core import Exception as Exc

if __name__ == "__main__":
    # Initialize ExceptionTracker
    tracker = Exc.ExceptionTracker()

    # Test get_exception_return
    try:
        1 / 0
    except Exception as e:
        exc_info = tracker.get_exception_return(error=e, user_input="1 / 0", params=((), {}), mask_tuple=(False, False, False, False))
        print("Exception Info:", exc_info)

    print("\n\n ------- masked ------- \n\n")
    # Test get_exception_return with masking
    try:
        lst = [1, 2, 3]
        print(lst[5])
    except Exception as e:
        exc_info_masked = tracker.get_exception_return(error=e, user_input="lst[5]", params=((), {}), mask_tuple=(True, True, True, True))
        print("Masked Exception Info:", exc_info_masked)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")