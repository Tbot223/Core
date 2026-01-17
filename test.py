"""
Test script for GlobalVars shared memory functionality.
Tests basic operations, race condition handling, and edge cases.
"""

import time
import threading
import pickle
from multiprocessing import Process, Lock as MPLock
from tbot223_core.Utils import GlobalVars

# ============================================
# Basic Shared Memory Tests
# ============================================

def test_basic_shm_operations():
    """Test basic shared memory operations: create, sync, update, close."""
    print("\n" + "="*60)
    print("TEST 1: Basic Shared Memory Operations")
    print("="*60)
    
    gv = GlobalVars(is_logging_enabled=False)
    shm_name = "test_shm_basic"
    
    # 1. Create shared memory
    print("\n[1] Creating shared memory...")
    result = gv.shm_gen(name=shm_name, size=4096, create_lock=False)
    print(f"    Result: {result.success}, Message: {result.data}")
    
    # 2. Set some variables
    print("\n[2] Setting variables...")
    gv.set("key1", "value1", overwrite=True)
    gv.set("key2", 12345, overwrite=True)
    gv.set("key3", {"nested": "dict"}, overwrite=True)
    gv.set("key4", [1, 2, 3, "list"], overwrite=True)
    print(f"    Variables: {gv.list_vars().data}")
    
    # 3. Sync to shared memory
    print("\n[3] Syncing to shared memory...")
    result = gv.shm_sync(shm_name)
    print(f"    Result: {result.success}, Message: {result.data}")
    
    # 4. Create another GlobalVars instance and update from shared memory
    print("\n[4] Creating new GlobalVars instance and updating from shared memory...")
    gv2 = GlobalVars(is_logging_enabled=False)
    result = gv2.shm_update(shm_name)
    print(f"    Result: {result.success}, Message: {result.data}")
    print(f"    gv2 Variables: {gv2.list_vars().data}")
    print(f"    gv2['key1']: {gv2.get('key1').data}")
    print(f"    gv2['key2']: {gv2.get('key2').data}")
    print(f"    gv2['key3']: {gv2.get('key3').data}")
    print(f"    gv2['key4']: {gv2.get('key4').data}")
    
    # 5. Verify data integrity
    print("\n[5] Verifying data integrity...")
    integrity_ok = (
        gv2.get('key1').data == "value1" and
        gv2.get('key2').data == 12345 and
        gv2.get('key3').data == {"nested": "dict"} and
        gv2.get('key4').data == [1, 2, 3, "list"]
    )
    print(f"    Data integrity: {'✓ PASSED' if integrity_ok else '✗ FAILED'}")
    
    # 6. Close shared memory
    print("\n[6] Closing shared memory...")
    result = gv.shm_close(shm_name)
    print(f"    Result: {result.success}, Message: {result.data}")
    
    print("\n" + "-"*60)
    print("TEST 1 COMPLETED")
    print("-"*60)
    return integrity_ok

# ============================================
# Multi-Process Writer/Reader Tests
# ============================================

def worker_writer(shm_name: str, worker_id: int, iterations: int):
    """Worker process that writes to shared memory."""
    gv = GlobalVars(is_logging_enabled=False)
    gv.shm_connect(shm_name)  # Connect to existing shm
    
    for i in range(iterations):
        gv.set(f"worker_{worker_id}_iter_{i}", f"value_{i}", overwrite=True)
        gv.set(f"counter_{worker_id}", i, overwrite=True)
        try:
            gv.shm_sync(shm_name)
        except Exception as e:
            print(f"    [Writer {worker_id}] Sync error at iteration {i}: {e}")
        time.sleep(0.01)
    
    print(f"    [Writer {worker_id}] Completed {iterations} iterations")

def worker_reader(shm_name: str, worker_id: int, iterations: int):
    """Worker process that reads from shared memory."""
    gv = GlobalVars(is_logging_enabled=False)
    gv.shm_connect(shm_name)  # Connect to existing shm
    
    successful_reads = 0
    for i in range(iterations):
        try:
            gv.shm_update(shm_name)
            successful_reads += 1
        except Exception as e:
            print(f"    [Reader {worker_id}] Update error at iteration {i}: {e}")
        time.sleep(0.005)
    
    print(f"    [Reader {worker_id}] Completed {successful_reads}/{iterations} successful reads")
    print(f"    [Reader {worker_id}] Final variables count: {len(gv.list_vars().data)}")

def test_multiprocess_read_write():
    """Test concurrent read/write operations with multiple processes."""
    print("\n" + "="*60)
    print("TEST 2: Multi-Process Read/Write Test")
    print("="*60)
    
    shm_name = "test_shm_multiproc"
    num_writers = 3
    num_readers = 3
    iterations = 20
    
    # Create shared memory in main process
    gv_main = GlobalVars(is_logging_enabled=False)
    result = gv_main.shm_gen(name=shm_name, size=65536, create_lock=False)
    print(f"\n[1] Created shared memory: {result.success}")
    
    # Initialize with some data
    gv_main.set("init_key", "init_value", overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[2] Starting {num_writers} writer processes and {num_readers} reader processes...")
    print(f"    Each process will perform {iterations} iterations\n")
    
    # Create writer and reader processes
    writers = []
    readers = []
    
    for i in range(num_writers):
        p = Process(target=worker_writer, args=(shm_name, i, iterations))
        writers.append(p)
    
    for i in range(num_readers):
        p = Process(target=worker_reader, args=(shm_name, i, iterations))
        readers.append(p)
    
    # Start all processes
    start_time = time.time()
    for p in writers + readers:
        p.start()
    
    # Wait for all processes to complete
    for p in writers + readers:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    print(f"\n[3] All processes completed in {elapsed_time:.2f} seconds")
    
    # Check final state
    gv_main.shm_update(shm_name)
    final_vars = gv_main.list_vars().data
    print(f"[4] Final variables count in main process: {len(final_vars)}")
    
    # Cleanup
    print("\n[5] Cleaning up shared memory...")
    result = gv_main.shm_close(shm_name)
    print(f"    Cleanup result: {result.success}")
    
    print("\n" + "-"*60)
    print("TEST 2 COMPLETED")
    print("-"*60)
    return True

# ============================================
# Thread-Safe Local Operations Test
# ============================================

def test_thread_safe_local_operations():
    """Test concurrent set operations on GlobalVars (thread-safe lock test)."""
    print("\n" + "="*60)
    print("TEST 3: Thread-Safe Local Operations Test")
    print("="*60)
    
    gv = GlobalVars(is_logging_enabled=False)
    num_threads = 10
    iterations_per_thread = 100
    
    def thread_worker(thread_id: int):
        for i in range(iterations_per_thread):
            gv.set(f"thread_{thread_id}_key_{i}", f"value_{i}", overwrite=True)
    
    print(f"\n[1] Starting {num_threads} threads, each performing {iterations_per_thread} set operations...")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=thread_worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed_time = time.time() - start_time
    
    expected_vars = num_threads * iterations_per_thread
    actual_vars = len(gv.list_vars().data)
    
    print(f"\n[2] All threads completed in {elapsed_time:.4f} seconds")
    print(f"[3] Expected variables: {expected_vars}")
    print(f"[4] Actual variables: {actual_vars}")
    
    passed = expected_vars == actual_vars
    print(f"[5] Test {'✓ PASSED' if passed else '✗ FAILED'}")
    
    print("\n" + "-"*60)
    print("TEST 3 COMPLETED")
    print("-"*60)
    return passed

# ============================================
# Shared Memory Size Limit Test
# ============================================

def test_shm_size_limit():
    """Test shared memory size limit handling."""
    print("\n" + "="*60)
    print("TEST 4: Shared Memory Size Limit Test")
    print("="*60)
    
    gv = GlobalVars(is_logging_enabled=False)
    shm_name = "test_shm_size"
    requested_size = 4096
    
    print(f"\n[1] Creating shared memory (requested: {requested_size} bytes)...")
    result = gv.shm_gen(name=shm_name, size=requested_size, create_lock=False)
    print(f"    Result: {result.success}")
    
    # Get actual allocated size
    shm_result = gv.shm_get(shm_name)
    actual_size = 0
    if shm_result.success:
        actual_size = shm_result.data.size
        print(f"    Allocated size: {actual_size} bytes")
    
    print("\n[2] Adding massive unique data to exceed allocated size...")
    import secrets
    for i in range(100):
        random_data = secrets.token_hex(512)
        gv.set(f"unique_key_{i}", random_data, overwrite=True)
    
    serialized_size = len(pickle.dumps(gv._GlobalVars__vars__))
    print(f"    Serialized size: {serialized_size} bytes")
    print(f"    Actual shared memory size: {actual_size} bytes")
    print(f"    Will exceed: {serialized_size + 8 > actual_size}")
    
    print("\n[3] Attempting to sync...")
    result = gv.shm_sync(shm_name)
    print(f"    Result success: {result.success}")
    
    passed = not result.success  # We expect failure
    if not result.success:
        print(f"    ✓ Error handled correctly!")
    else:
        print("    ✗ Sync succeeded unexpectedly (data should have exceeded space)")
    
    print("\n[4] Cleaning up...")
    gv.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 4 COMPLETED")
    print("-"*60)
    return passed

# ============================================
# Race Condition Test (Without Lock)
# ============================================

def worker_increment_no_lock(shm_name: str, worker_id: int, iterations: int):
    """Worker that reads, increments, and writes counter (no lock - race condition expected)."""
    gv = GlobalVars(is_logging_enabled=False)
    gv.shm_connect(shm_name)  # Connect to existing shm
    
    for i in range(iterations):
        gv.shm_update(shm_name)
        current = gv.get("counter").data
        new_value = current + 1
        gv.set("counter", new_value, overwrite=True)
        gv.shm_sync(shm_name)
    
    print(f"    [Worker {worker_id}] Completed {iterations} increments (no lock)")

def test_race_condition_without_lock():
    """Test race condition with concurrent read-modify-write (no lock)."""
    print("\n" + "="*60)
    print("TEST 5: Race Condition Test (Without Lock)")
    print("="*60)
    
    shm_name = "test_shm_race_nolock"
    num_processes = 4
    iterations_per_process = 50
    expected_final_value = num_processes * iterations_per_process
    
    gv_main = GlobalVars(is_logging_enabled=False)
    gv_main.shm_gen(name=shm_name, size=4096, create_lock=False)
    gv_main.set("counter", 0, overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[1] Initial counter value: {gv_main.get('counter').data}")
    print(f"[2] Starting {num_processes} processes, each incrementing {iterations_per_process} times")
    print(f"[3] Expected final value (if no race): {expected_final_value}")
    
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = Process(target=worker_increment_no_lock, args=(shm_name, i, iterations_per_process))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    gv_main.shm_update(shm_name)
    final_value = gv_main.get("counter").data
    lost_updates = expected_final_value - final_value
    
    print(f"\n[4] All processes completed in {elapsed_time:.2f} seconds")
    print(f"[5] Final counter value: {final_value}")
    print(f"[6] Expected value: {expected_final_value}")
    print(f"[7] Lost updates: {lost_updates}")
    
    if final_value == expected_final_value:
        print("\n    ✓ No data loss (lucky run or fast execution)")
    else:
        print(f"\n    ⚠ RACE CONDITION DEMONSTRATED - {lost_updates} updates lost")
        print("    This is expected behavior without inter-process locking.")
    
    gv_main.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 5 COMPLETED")
    print("-"*60)
    return True  # This test demonstrates race condition, not pass/fail

# ============================================
# Race Condition Test (With Lock)
# ============================================

def worker_increment_with_lock(args):
    """Worker that uses shared multiprocessing.Lock for synchronization."""
    shm_name, worker_id, iterations, shm_lock = args
    gv = GlobalVars(is_logging_enabled=False)
    gv.shm_connect(shm_name)  # Connect to existing shm
    
    for i in range(iterations):
        with shm_lock:
            gv.shm_update(shm_name)
            current = gv.get("counter").data
            gv.set("counter", current + 1, overwrite=True)
            gv.shm_sync(shm_name)
    
    print(f"    [Worker {worker_id}] Completed {iterations} increments (with lock)")

def test_race_condition_with_lock():
    """Test concurrent read-modify-write with shared multiprocessing.Lock."""
    print("\n" + "="*60)
    print("TEST 6: Race Condition Test (With Lock)")
    print("="*60)
    
    shm_name = "test_shm_race_lock"
    num_processes = 4
    iterations_per_process = 50
    expected_final_value = num_processes * iterations_per_process
    
    gv_main = GlobalVars(is_logging_enabled=False)
    result = gv_main.shm_gen(name=shm_name, size=4096, create_lock=True)
    shm_lock = result.data  # Get the shared lock
    
    gv_main.set("counter", 0, overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[1] Initial counter value: {gv_main.get('counter').data}")
    print(f"[2] Starting {num_processes} processes with shared multiprocessing.Lock")
    print(f"[3] Expected final value: {expected_final_value}")
    
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = Process(target=worker_increment_with_lock, args=((shm_name, i, iterations_per_process, shm_lock),))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    gv_main.shm_update(shm_name)
    final_value = gv_main.get("counter").data
    
    print(f"\n[4] All processes completed in {elapsed_time:.2f} seconds")
    print(f"[5] Final counter value: {final_value}")
    print(f"[6] Expected value: {expected_final_value}")
    
    passed = final_value == expected_final_value
    if passed:
        print("\n    ✓ TEST PASSED - Lock prevented data loss!")
    else:
        print(f"\n    ✗ TEST FAILED - {expected_final_value - final_value} updates lost")
    
    gv_main.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 6 COMPLETED")
    print("-"*60)
    return passed

# ============================================
# Edge Cases Test
# ============================================

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*60)
    print("TEST 7: Edge Cases and Error Handling")
    print("="*60)
    
    gv = GlobalVars(is_logging_enabled=False)
    all_passed = True
    
    # Test 1: Empty shared memory update
    print("\n[1] Testing empty shared memory update...")
    shm_name = "test_shm_edge"
    gv.shm_gen(name=shm_name, size=1024, create_lock=False)
    result = gv.shm_update(shm_name)
    print(f"    Result: {result.success}, Message: {result.data}")
    gv.shm_close(shm_name)
    
    # Test 2: Various data types
    print("\n[2] Testing various data types...")
    shm_name = "test_shm_types"
    gv2 = GlobalVars(is_logging_enabled=False)
    gv2.shm_gen(name=shm_name, size=8192, create_lock=False)
    
    test_data = {
        "int": 42,
        "float": 3.14159,
        "str": "hello world",
        "bytes": b"binary data",
        "list": [1, 2, 3, [4, 5]],
        "dict": {"a": 1, "b": {"c": 2}},
        "tuple": (1, 2, 3),
        "set": {1, 2, 3},
        "none": None,
        "bool_true": True,
        "bool_false": False,
    }
    
    for key, value in test_data.items():
        gv2.set(key, value, overwrite=True)
    
    gv2.shm_sync(shm_name)
    
    gv3 = GlobalVars(is_logging_enabled=False)
    gv3.shm_update(shm_name)
    
    types_ok = True
    for key, expected in test_data.items():
        actual = gv3.get(key).data
        if actual != expected:
            print(f"    ✗ Type mismatch for '{key}': expected {expected}, got {actual}")
            types_ok = False
            all_passed = False
    
    if types_ok:
        print("    ✓ All data types preserved correctly")
    
    gv2.shm_close(shm_name)
    
    # Test 3: Special characters in keys
    print("\n[3] Testing special characters in keys...")
    shm_name = "test_shm_special"
    gv4 = GlobalVars(is_logging_enabled=False)
    gv4.shm_gen(name=shm_name, size=4096, create_lock=False)
    
    special_keys = [
        "key with spaces",
        "key_with_underscore",
        "key-with-dash",
        "key.with.dots",
        "한글키",
        "キー日本語",
        "emoji_key_🔑",
    ]
    
    for key in special_keys:
        gv4.set(key, f"value_for_{key}", overwrite=True)
    
    gv4.shm_sync(shm_name)
    
    gv5 = GlobalVars(is_logging_enabled=False)
    gv5.shm_update(shm_name)
    
    special_ok = True
    for key in special_keys:
        result = gv5.get(key)
        if not result.success or result.data != f"value_for_{key}":
            print(f"    ✗ Special key failed: '{key}'")
            special_ok = False
            all_passed = False
    
    if special_ok:
        print("    ✓ All special character keys work correctly")
    
    gv4.shm_close(shm_name)
    
    # Test 4: Large value
    print("\n[4] Testing large value storage...")
    shm_name = "test_shm_large"
    gv6 = GlobalVars(is_logging_enabled=False)
    gv6.shm_gen(name=shm_name, size=1024*1024, create_lock=False)  # 1MB
    
    large_value = "x" * 100000  # 100KB string
    gv6.set("large_key", large_value, overwrite=True)
    gv6.shm_sync(shm_name)
    
    gv7 = GlobalVars(is_logging_enabled=False)
    gv7.shm_update(shm_name)
    
    retrieved = gv7.get("large_key").data
    large_ok = retrieved == large_value
    if large_ok:
        print(f"    ✓ Large value (100KB) stored and retrieved correctly")
    else:
        print(f"    ✗ Large value mismatch")
        all_passed = False
    
    gv6.shm_close(shm_name)
    
    print(f"\n[5] Overall edge cases: {'✓ ALL PASSED' if all_passed else '✗ SOME FAILED'}")
    
    print("\n" + "-"*60)
    print("TEST 7 COMPLETED")
    print("-"*60)
    return all_passed

# ============================================
# Cache Management Test
# ============================================

def test_shm_cache_management():
    """Test shared memory cache management."""
    print("\n" + "="*60)
    print("TEST 8: Shared Memory Cache Management")
    print("="*60)
    
    gv = GlobalVars(is_logging_enabled=False)
    shm_names = []
    
    print("\n[1] Creating multiple shared memory objects...")
    for i in range(7):
        shm_name = f"test_cache_{i}"
        shm_names.append(shm_name)
        gv.shm_gen(name=shm_name, size=1024, create_lock=False)
        gv.set(f"data_{i}", f"value_{i}", overwrite=True)
        gv.shm_sync(shm_name)
        print(f"    Created: {shm_name}")
    
    print("\n[2] Checking cache behavior...")
    # Access older entries to test LRU behavior
    for name in shm_names:
        result = gv.shm_get(name)
        print(f"    Accessing {name}: {result.success}")
    
    print("\n[3] Cleaning up all shared memory objects...")
    for name in shm_names:
        try:
            gv.shm_close(name)
            print(f"    Closed: {name}")
        except Exception as e:
            print(f"    Error closing {name}: {e}")
    
    print("\n" + "-"*60)
    print("TEST 8 COMPLETED")
    print("-"*60)
    return True

# ============================================
# Stress Test
# ============================================

def worker_stress(shm_name: str, worker_id: int, iterations: int, shm_lock):
    """Stress test worker with rapid read-modify-write cycles."""
    gv = GlobalVars(is_logging_enabled=False)
    gv.shm_connect(shm_name)  # Connect to existing shm
    
    for i in range(iterations):
        with shm_lock:
            gv.shm_update(shm_name)
            current = gv.get("stress_counter").data
            gv.set("stress_counter", current + 1, overwrite=True)
            gv.set(f"worker_{worker_id}_last", i, overwrite=True)
            gv.shm_sync(shm_name)
    
    print(f"    [Stress Worker {worker_id}] Completed {iterations} iterations")

def test_stress():
    """Stress test with many rapid operations."""
    print("\n" + "="*60)
    print("TEST 9: Stress Test (Rapid Operations)")
    print("="*60)
    
    shm_name = "test_shm_stress"
    num_processes = 8
    iterations_per_process = 100
    expected_total = num_processes * iterations_per_process
    
    gv_main = GlobalVars(is_logging_enabled=False)
    result = gv_main.shm_gen(name=shm_name, size=65536, create_lock=True)
    shm_lock = result.data
    
    gv_main.set("stress_counter", 0, overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[1] Starting stress test:")
    print(f"    Processes: {num_processes}")
    print(f"    Iterations per process: {iterations_per_process}")
    print(f"    Total operations: {expected_total}")
    
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = Process(target=worker_stress, args=(shm_name, i, iterations_per_process, shm_lock))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    gv_main.shm_update(shm_name)
    final_counter = gv_main.get("stress_counter").data
    ops_per_second = expected_total / elapsed_time
    
    print(f"\n[2] Results:")
    print(f"    Time elapsed: {elapsed_time:.2f} seconds")
    print(f"    Final counter: {final_counter}")
    print(f"    Expected: {expected_total}")
    print(f"    Operations/second: {ops_per_second:.0f}")
    
    passed = final_counter == expected_total
    print(f"\n[3] {'✓ TEST PASSED' if passed else '✗ TEST FAILED'}")
    
    gv_main.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 9 COMPLETED")
    print("-"*60)
    return passed

# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("GLOBALVARS SHARED MEMORY TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results["Basic Operations"] = test_basic_shm_operations()
    results["Multi-Process R/W"] = test_multiprocess_read_write()
    results["Thread-Safe Local"] = test_thread_safe_local_operations()
    results["Size Limit"] = test_shm_size_limit()
    results["Race (No Lock)"] = test_race_condition_without_lock()
    results["Race (With Lock)"] = test_race_condition_with_lock()
    results["Edge Cases"] = test_edge_cases()
    results["Cache Management"] = test_shm_cache_management()
    results["Stress Test"] = test_stress()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-"*60)
    print(f"Total: {passed} passed, {failed} failed")
    print("="*60 + "\n")
