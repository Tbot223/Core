from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # Test atomic write
    fm.atomic_write("atomic_test.txt", "This is an atomic write test.")

    # Verify the content was written correctly
    content = fm.read_file("atomic_test.txt")
    print("File Content:", content.data)

    # Test atomic write with not existing directory
    fm.atomic_write("non_existing_dir/atomic_test2.txt", "This is another atomic write test.")
    
    # Verify the content was written correctly
    content2 = fm.read_file("non_existing_dir/atomic_test2.txt")
    print("File Content 2:", content2.data)

    # Cleanup test files
    res = []
    res.append(fm.delete_file("atomic_test.txt"))
    res.append(fm.delete_directory("non_existing_dir"))
    for r in res:
        print("Cleanup result: ", r.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")