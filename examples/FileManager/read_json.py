from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager.FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # Define the JSON file path
    json_file_path = BASE_DIR / "sample_data.json"

    # Ensure the JSON file exists for demonstration purposes
    sample_data = {
        "name": "Test",
        "value": 123,
        "items": ["item1", "item2", "item3"]
    }
    fm.write_json(json_file_path, sample_data)

    # Read JSON file
    data = fm.read_json(json_file_path)

    # Verify the content
    print("Read JSON Data:", data.data)

    # Cleanup: remove the sample JSON file
    fm.delete_file(json_file_path)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")