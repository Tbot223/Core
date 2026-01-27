# external Modules
import pytest

# internal Modules
from tbot223_core import Exception

@pytest.fixture(scope="module")
def tracker():
    """
    Fixture to create an ExceptionTracker instance for testing.
    """
    return Exception.ExceptionTracker()

@pytest.mark.usefixtures("tracker")
class TestExceptionTracker:
    def zero_division(self) -> None:
        """
        A method that raises a ZeroDivisionError for testing.
        """
        return 1 / 0
    
    def test_get_exception_location(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_location method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_location(error)
        assert result.success is True
        assert "line" in result.data
        assert "in" in result.data

    def test_get_exception_info(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_info method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_info(error)
        assert result.success is True
        assert result.data["error"]["type"] == "ZeroDivisionError"

        with pytest.raises(ZeroDivisionError) as exc_masking:
            self.zero_division()

        error_masking = exc_masking.value
        result_masking = tracker.get_exception_info(error_masking, masking=True)
        assert result_masking.success is True
        assert result_masking.data["computer_info"] == "<Masked>"

    def test_get_exception_return(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test the get_exception_return method of ExceptionTracker.
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()

        error = exc_info.value
        result = tracker.get_exception_return(error)
        assert result.success is False
        assert result.data["error"]["type"] == "ZeroDivisionError"

        with pytest.raises(ZeroDivisionError) as exc_masking:
            self.zero_division()

        error_masking = exc_masking.value
        result_masking = tracker.get_exception_return(error_masking, masking=True)
        assert result_masking.success is False
        assert result_masking.data == "<Masked>"

    def test_system_info_initialization(self) -> None:
        """
        Test that the system info is initialized correctly in ExceptionTracker.
        """
        tracker = Exception.ExceptionTracker()
        assert isinstance(tracker._system_info, dict)
        assert "OS" in tracker._system_info
        assert "Python_Version" in tracker._system_info

    @Exception.ExceptionTrackerDecorator(masking=False, tracker=Exception.ExceptionTracker())
    def dummy_method(self, x: int) -> str:
        """
        A dummy method to test the ExceptionTrackerDecorator.
        """
        return 10 / x

    def test_exception_tracker_decorator(self) -> None:
        """
        Test the ExceptionTrackerDecorator.
        """
        result = self.dummy_method(0)
        
        assert result.data["error"]["type"] == "ZeroDivisionError"
    
    def test_get_exception_info_with_params(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test get_exception_info with user_input and params
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()
        
        error = exc_info.value
        result = tracker.get_exception_info(
            error, 
            user_input="test_input", 
            params=((1, 2), {"key": "value"})
        )
        
        assert result.success is True
        assert result.data["input_context"]["user_input"] == "test_input"
        assert result.data["input_context"]["params"]["args"] == (1, 2)
        assert result.data["input_context"]["params"]["kwargs"] == {"key": "value"}
    
    def test_get_exception_return_with_params(self, tracker: Exception.ExceptionTracker) -> None:
        """
        Test get_exception_return with params
        """
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.zero_division()
        
        error = exc_info.value
        result = tracker.get_exception_return(
            error,
            params=((10,), {"divisor": 0})
        )
        
        assert result.success is False
        assert "ZeroDivisionError" in result.data["error"]["type"]
    
    @Exception.ExceptionTrackerDecorator(masking=True, tracker=Exception.ExceptionTracker())
    def dummy_method_masked(self, x: int) -> str:
        """
        A dummy method to test the ExceptionTrackerDecorator with masking.
        """
        return 10 / x
    
    def test_exception_tracker_decorator_with_masking(self) -> None:
        """
        Test the ExceptionTrackerDecorator with masking enabled.
        """
        result = self.dummy_method_masked(0)
        
        assert result.success is False
        assert result.data == "<Masked>"
    
    @Exception.ExceptionTrackerDecorator(masking=False, tracker=Exception.ExceptionTracker())
    def successful_method(self, x: int) -> int:
        """
        A method that succeeds for testing decorator.
        """
        return x * 2
    
    def test_exception_tracker_decorator_success(self) -> None:
        """
        Test that ExceptionTrackerDecorator returns normal value on success.
        """
        result = self.successful_method(5)
        
        assert result == 10  # Normal return value, not wrapped


@pytest.mark.usefixtures("tracker")
class TestExceptionEdgeCases:
    """Edge case tests for Exception module"""
    
    def test_exception_with_none_traceback(self, tracker: Exception.ExceptionTracker) -> None:
        """Test handling exception with no traceback"""
        error = ValueError("Test error without traceback")
        # Manually set traceback to None
        error.__traceback__ = None
        
        # Should handle gracefully
        result = tracker.get_exception_location(error)
        # May fail but should not crash
    
    def test_exception_info_all_system_fields(self, tracker: Exception.ExceptionTracker) -> None:
        """Test that all system info fields are present"""
        expected_fields = [
            "OS", "OS_version", "Release", "Architecture", 
            "Processor", "Python_Version", "Python_Executable", 
            "Current_Working_Directory"
        ]
        
        for field in expected_fields:
            assert field in tracker._system_info, f"Missing field: {field}"
    
    def test_exception_info_timestamp_format(self, tracker: Exception.ExceptionTracker) -> None:
        """Test that timestamp is in correct format"""
        error = None
        try:
            1 / 0
        except ZeroDivisionError as e:
            error = e
        
        result = tracker.get_exception_info(error)
        timestamp = result.data["timestamp"]
        # Should be in YYYY-MM-DD HH:MM:SS format
        assert len(timestamp) == 19
        assert timestamp[4] == "-" and timestamp[7] == "-"
        assert timestamp[10] == " "
        assert timestamp[13] == ":" and timestamp[16] == ":"

if __name__ == "__main__":
    pytest.main([__file__])