from pathlib import Path
from tbot223_core import AppCore
import time

def main():
    # Simple menu to choose between restart and exit
    # Why did you make it? -> To prevent the program from restarting endlessly during testing
    while True:
        print("1. Restart Application")
        print("2. Exit Application")
        choice = input("Select an option (1 or 2): ")
        if choice == '1':
            return True
        elif choice == '2':
            return False
        else:
            print("Invalid choice. Please try again.\n")

# Define base directory
BASE_DIR = Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize AppCore
    ap = AppCore.AppCore(is_logging_enabled=True, base_dir=BASE_DIR)

    if main():
        print("Restarting application in 3 seconds...")
        time.sleep(3)

        # Restart application
        ap.restart_application(pause=True)
    else:
        print("Exiting application...")
        ap.exit_application(code=0, pause=True)

    # This line will not be reached if restart_application works correctly
    print("\n -------------- \n TEST COMPLETE \n -------------- \n")