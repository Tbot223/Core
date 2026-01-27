from pathlib import Path
from tbot223_core import AppCore

# Define base directory
BASE_DIR = Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize AppCore
    ap = AppCore.AppCore(is_logging_enabled=True, base_dir=BASE_DIR)

    print("Exiting application...")

    # Exit application
    ap.exit_application(code=0, pause=True)

    # This line will not be reached if exit_application works correctly
    print("\n -------------- \n TEST COMPLETE \n -------------- \n")