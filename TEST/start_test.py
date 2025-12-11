# external Modules
import pytest
from pathlib import Path

# internal Modules
from SRC import AppCore_test, Exception_test, LogSys_test, Utils_test, FileManager_test
from tbot223_core import FileManager

class Test_CoreV2:
    def test_AppCore(self):
        pytest.main([AppCore_test.__file__, "-m not performance"])

    def test_Exception(self):
        pytest.main([Exception_test.__file__])

    def test_LogSys(self):
        pytest.main([LogSys_test.__file__])

    def test_Utils(self):
        pytest.main([Utils_test.__file__])

    def test_FileManager(self):
        pytest.main([FileManager_test.__file__])

    def run_all_tests(self, include_performance=False, duration=False):
        pytest.main([str(Path(__file__).resolve().parent / "SRC"), "-v", "" if include_performance else "-m not performance", "--durations=10" if duration else ""])

if __name__ == "__main__":
    performance_test = input("Do you want to run performance tests? (y/n): ").strip().lower()
    show_run_duration = input("Do you want to see the test run duration? (y/n): ").strip().lower()
    duration = show_run_duration == 'y'
    include_performance = performance_test == 'y'
    log_del = input("Do you want to delete the log files after running the test? (**Caution** All existing logs will be deleted) (y/n): ").strip().lower()
    tester = Test_CoreV2()
    tester.run_all_tests(include_performance=include_performance, duration=duration)
    if log_del == 'y':
        log_dir = Path(__file__).resolve().parent / "SRC" / "logs"
        with FileManager.FileManager(is_logging_enabled=False) as FM:
            if log_dir.exists() and log_dir.is_dir():
                for item in log_dir.iterdir():
                    FM.delete_directory(item)
            else:
                print(f"No log directory found at: {log_dir}")
