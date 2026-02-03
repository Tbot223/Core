# external Modules
import pytest
from pathlib import Path

# internal Modules
from tbot223_core.LogSys import LoggerManager, Log
from tbot223_core import LogSys

@pytest.fixture(scope="module")
def setup_module(tmp_path_factory):
    """
    Fixture to create a LoggerManager instance for testing.
    """
    tmp_path = tmp_path_factory.mktemp("test")
    return LoggerManager(base_dir=tmp_path / "logs", second_log_dir="test_logs"), Log()

@pytest.mark.usefixtures("setup_module")
class TestLogSys:
    def test_make_logger(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "test_logger"
        log_level = "DEBUG"

        # Test creating a logger
        result = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert result.success, f"Logger creation failed: {result.error}"
        assert logger_name in logger_manager._loggers.keys(), "Logger not found in manager after creation."

        # Test creating the same logger again
        result_duplicate = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert not result_duplicate.success, "Duplicate logger creation should have failed."

    def test_get_logger(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "test_logger_get"
        log_level = "INFO"

        # Get logger ( already created )
        get_result = logger_manager.get_logger(logger_name=logger_name)
        assert not get_result.success, "Getting non-existent logger should have failed."

    def test_log_functionality(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "functional_logger"
        log_level = "INFO"

        # Create logger
        create_result = logger_manager.make_logger(logger_name=logger_name, log_level=log_level)
        assert create_result.success, f"Logger creation failed: {create_result.error}"

        # Get logger
        get_result = logger_manager.get_logger(logger_name=logger_name)
        assert get_result.success, f"Getting logger failed: {get_result.error}"
        log.logger = get_result.data

        # Test logging
        try:
            log.log_message("INFO", "This is an info message.")
            log.log_message("WARNING", "This is a warning message.")
            log.log_message("ERROR", "This is an error message.")
        except Exception as e:
            pytest.fail(f"Logging functionality failed with exception: {e}")

@pytest.mark.usefixtures("setup_module")
class TestLogSysEdgeCases:
    def test_invalid_log_level(self, setup_module):
        logger_manager, log = setup_module
        logger_name = "invalid_level_logger"
        invalid_log_level = "INVALID_LEVEL"

        # Test creating a logger with invalid log level
        result = logger_manager.make_logger(logger_name=logger_name, log_level=invalid_log_level)
        assert not result.success, "Logger creation with invalid log level should have failed."

    def test_log_without_logger(self, setup_module):
        """Test logging when logger is not initialized"""
        _, log = setup_module
        
        # Create a new Log instance without logger
        empty_log = Log(logger=None)
        result = empty_log.log_message("INFO", "Test message")
        assert not result.success, "Logging without logger should fail"
    
    def test_log_message_levels(self, setup_module):
        """Test all log message levels"""
        logger_manager, _ = setup_module
        
        # Create a new logger for this test
        logger_name = "level_test_logger"
        logger_manager.make_logger(logger_name=logger_name, log_level="DEBUG")
        logger = logger_manager.get_logger(logger_name).data
        log = Log(logger=logger)
        
        # Test all levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            result = log.log_message(level, f"Test message for {level}")
            assert result.success, f"Logging at {level} level should succeed"
    
    def test_stop_stream_handlers(self, setup_module):
        """Test stopping stream handlers"""
        logger_manager, _ = setup_module
        
        logger_name = "stream_test_logger"
        logger_manager.make_logger(logger_name=logger_name, log_level="DEBUG")
        
        # Get the actual logger first
        logger = logger_manager.get_logger(logger_name).data
        
        # Stop stream handlers using the logger object
        result = logger_manager.stop_stream_handlers(logger)
        assert result.success, f"Stopping stream handlers failed: {result.error}"
    
    def test_stop_stream_handlers_nonexistent(self, setup_module):
        """Test stopping stream handlers for nonexistent logger"""
        logger_manager, _ = setup_module
        
        # Pass None which should fail
        result = logger_manager.stop_stream_handlers(None)
        assert not result.success, "Stopping handlers for None logger should fail"


@pytest.mark.usefixtures("setup_module")
class TestSimpleSetting:
    """Tests for SimpleSetting class"""
    
    def test_simple_setting_initialization(self, tmp_path):
        """Test SimpleSetting initialization"""
        setting = LogSys.SimpleSetting(
            base_dir=tmp_path / "logs",
            second_log_dir="test",
            logger_name="simple_logger"
        )
        
        logger_manager, log, logger = setting.get_instance()
        
        assert logger_manager is not None, "LoggerManager should be initialized"
        assert log is not None, "Log should be initialized"
        assert logger is not None, "Logger should be initialized"
    
    def test_simple_setting_logging(self, tmp_path):
        """Test logging with SimpleSetting"""
        setting = LogSys.SimpleSetting(
            base_dir=tmp_path / "logs",
            second_log_dir="test",
            logger_name="simple_log_test"
        )
        
        _, log, _ = setting.get_instance()
        
        result = log.log_message("INFO", "Test message from SimpleSetting")
        assert result.success, f"Logging with SimpleSetting failed: {result.error}"

    # I WILL ADD MORE EDGE CASE TESTS HERE IN THE FUTURE

if __name__ == "__main__":
    pytest.main([__file__])
