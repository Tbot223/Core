from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # Create a new directory
    fm.create_directory(BASE_DIR / "NewDirectory")

    # Verify creation
    if (BASE_DIR / "NewDirectory").exists():
        print("Directory created successfully.")
    else:
        print("Failed to create directory.")

    # Clean up by removing the created directory
    fm.delete_directory(BASE_DIR / "NewDirectory")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")