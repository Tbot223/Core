from tbot223_core.Result import Result

if __name__ == "__main__":
    # How to use Result class
    # Creating a successful Result
    success_result = Result(True, None, "Operation completed successfully.", data={"key": "value"}) # data can be any type

    print("Success Result:")
    print("Success:", success_result.success)
    print("Error:", success_result.error)
    print("Context:", success_result.context)
    print("Data:", success_result.data)

    # Creating a failed Result
    failed_result = Result(False, "An error occurred.", "Operation failed due to an error.", data=None)
    print("\nFailed Result:")
    print("Success:", failed_result.success)
    print("Error:", failed_result.error)
    print("Context:", failed_result.context)
    print("Data:", failed_result.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")