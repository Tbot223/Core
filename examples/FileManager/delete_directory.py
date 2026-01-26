from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager.FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # make sure the directory exists for demonstration purposes
    fm.create_directory(BASE_DIR / "TestDirectory") 

    # existence check before deletion
    if (BASE_DIR / "TestDirectory").exists():
        print(f"Directory {BASE_DIR / 'TestDirectory'} exists. Proceeding to delete.")
    else:
        print(f"Directory {BASE_DIR / 'TestDirectory'} does not exist. Cannot delete.")

    # Delete the directory
    fm.delete_directory(BASE_DIR / "TestDirectory")

    # Verify deletion
    if not (BASE_DIR / "TestDirectory").exists():
        print("Directory deleted successfully.")
    else:
        print("Failed to delete directory.")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")