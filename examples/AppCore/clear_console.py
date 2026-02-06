from pathlib import Path
from tbot223_core import AppCore
import time

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize AppCore
    ap = AppCore(is_logging_enabled=True, base_dir=BASE_DIR)

    # dirty work to show the console clearing
    print("This is some text in the console.", end="\n\n")
    time.sleep(1)
    for i in range(10):
        if i == 9:
            print(f"Line {i+1} - Last line before clearing!", end="\n\n")
        else:
            print(f"Line {i+1}")
        time.sleep(0.2)
    
    time.sleep(1)
    print("Clearing console in 3 seconds...")
    time.sleep(3)

    # Clear console
    ap.clear_console()

    print("Console cleared!")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")