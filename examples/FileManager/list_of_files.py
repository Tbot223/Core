from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager.FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # sample file path
    sample_dir = BASE_DIR / "SampleDir"
    for i in range(5):
        fm.atomic_write(sample_dir / f"file_{i}.txt", f"This is sample file {i}.")
    for i in range(3):
        fm.atomic_write(sample_dir / f"document_{i}.doc", f"This is sample document {i}.")

    # List files in the directory
    files = fm.list_of_files(sample_dir)
    print("--- < List of files in directory > ---\n")
    for f in files.data:
        print(f)
    print("\n--------------------------------------\n")

    # List .txt files in the directory
    txt_files = fm.list_of_files(sample_dir, extensions=[".txt"])
    print("--- < List of .txt files in directory > ---")
    for f in txt_files.data:
        print(f)
    print("\n-----------------------------------------\n")

    # List .doc files in the directory
    doc_files = fm.list_of_files(sample_dir, extensions=[".doc"])
    print("--- < List of .doc files in directory > ---")
    for f in doc_files.data:
        print(f)
    print("\n-----------------------------------------\n")

    # Cleanup: remove the sample files and directory
    fm.delete_directory(sample_dir)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")