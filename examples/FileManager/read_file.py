from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager.FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # sample file path
    sample_file_path = BASE_DIR / "sample_text.txt"

    # Ensure the sample file exists for demonstration purposes
    fm.atomic_write(sample_file_path, "This is a sample text file for testing FileManager read functionality.")

    # Read the file
    content = fm.read_file(sample_file_path)

    # Verify the content
    print("Read File Content:", content)

    # Cleanup: remove the sample file
    fm.delete_file(sample_file_path)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")