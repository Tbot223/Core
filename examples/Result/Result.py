from tbot223_core.Result import Result

if __name__ == "__main__":
    # How to use Result class
    # Creating a successful Result
    success_result = Result(True, None, "Operation completed successfully.", data={"key": "value"}) # data can be any type

    print("Success Result:")
    print("Is Success:", success_result.is_success)
    print("Error:", success_result.error)
    print("Message:", success_result.message)
    print("Data:", success_result.data)

    # Creating a failed Result
    failed_result = Result(False, "An error occurred.", "Operation failed due to an error.", data=None)
    print("\nFailed Result:")
    print("Is Success:", failed_result.is_success)
    print("Error:", failed_result.error)
    print("Message:", failed_result.message)
    print("Data:", failed_result.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")