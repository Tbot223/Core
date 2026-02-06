from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # Define data to write
    data = {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }

    # Write JSON file
    fm.write_json("user_data.json", data, indent=0) # indent=0 for compact format

    print(f"JSON file 'user_data.json' written successfully in {BASE_DIR}")

    # Read back the file to verify
    read_data = fm.read_json("user_data.json").data
    print("Read back data:", read_data)

    #Define data to write in pretty format
    pretty_data = {
        "name": "Jane Smith",
        "age": 25,
        "city": "Los Angeles"
    }

    # Write JSON file in pretty format
    fm.write_json("pretty_user_data.json", pretty_data, indent=4) # indent=4 for pretty format

    print(f"JSON file 'pretty_user_data.json' written successfully in {BASE_DIR}")

    # Read back the pretty file to verify
    read_pretty_data = fm.read_json("pretty_user_data.json").data
    print("Read back pretty data:", read_pretty_data)

    # Cleanup: remove the created files
    fm.delete_file("user_data.json")
    fm.delete_file("pretty_user_data.json")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")