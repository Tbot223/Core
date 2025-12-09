from tbot223_core.Utils import Utils

def test_insert_at_intervals():
    print("Test: Insert at Intervals")

utils = Utils(is_logging_enabled=False)
data_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
data_str = "ABCDEFGHIJ"
result = utils.insert_at_intervals(data_str, 3, test_insert_at_intervals, at_start=False)
if result.success:
    print(result.data)
else:
    print(result.data)