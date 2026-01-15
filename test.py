"""
Test script for GlobalVars shared memory functionality.
Tests basic operations and race condition handling.
"""

import time
import multiprocessing
from multiprocessing import Process
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
    result = gv.shm_gen(name=shm_name, size=4096)
    print(f"    Result: {result.success}, Message: {result.data}")
    
    # 2. Set some variables
    print("\n[2] Setting variables...")
    gv.set("key1", "value1", overwrite=True)
    gv.set("key2", 12345, overwrite=True)
    gv.set("key3", {"nested": "dict"}, overwrite=True)
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
    
    # 5. Close shared memory
    print("\n[5] Closing shared memory...")
    result = gv.shm_close(shm_name)
    print(f"    Result: {result.success}, Message: {result.data}")
    
    print("\n" + "-"*60)
    print("TEST 1 COMPLETED")
    print("-"*60)

# ============================================
# Race Condition Tests
# ============================================

def worker_increment(shm_name: str, worker_id: int, iterations: int):
    """Worker that reads, increments, and writes counter (no lock)."""
    gv = GlobalVars(is_logging_enabled=False)
    
    for i in range(iterations):
        # Read current value from shared memory
        gv.shm_update(shm_name)
        current = gv.get("counter").data
        
        # Increment
        new_value = current + 1
        
        # Write back
        gv.set("counter", new_value, overwrite=True)
        gv.shm_sync(shm_name)
    
    print(f"    [Worker {worker_id}] Completed {iterations} increments")

def worker_increment_with_lock(args):
    """Worker that uses file lock for synchronization."""
    import fcntl
    shm_name, worker_id, iterations, lock_path = args
    gv = GlobalVars(is_logging_enabled=False)
    
    for i in range(iterations):
        # Acquire file lock
        with open(lock_path, 'w') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                # Critical section: read, modify, write
                gv.shm_update(shm_name)
                current = gv.get("counter").data
                new_value = current + 1
                gv.set("counter", new_value, overwrite=True)
                gv.shm_sync(shm_name)
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    
    print(f"    [Worker {worker_id}] Completed {iterations} locked increments")

def worker_increment_with_shm_lock(args):
    """Worker that uses shared multiprocessing.Lock for synchronization."""
    shm_name, worker_id, iterations, shm_lock = args
    gv = GlobalVars(is_logging_enabled=False)
    
    for i in range(iterations):
        with shm_lock:
            gv.shm_update(shm_name)
            current = gv.get("counter").data
            gv.set("counter", current + 1, overwrite=True)
            gv.shm_sync(shm_name)
    
    print(f"    [Worker {worker_id}] Completed {iterations} increments (shm_lock)")

def worker_increment_atomic(args):
    """Worker that uses shm_atomic_modify for synchronization."""
    shm_name, worker_id, iterations = args
    gv = GlobalVars(is_logging_enabled=False)
    
    for i in range(iterations):
        gv.shm_atomic_modify(shm_name, "counter", lambda x: x + 1)
    
    print(f"    [Worker {worker_id}] Completed {iterations} atomic increments")

def worker_writer(shm_name: str, worker_id: int, iterations: int):
    """Worker process that writes to shared memory."""
    gv = GlobalVars(is_logging_enabled=False)
    
    for i in range(iterations):
        gv.set(f"worker_{worker_id}_iter_{i}", f"value_{i}", overwrite=True)
        gv.set(f"counter_{worker_id}", i, overwrite=True)
        try:
            gv.shm_sync(shm_name)
        except Exception as e:
            print(f"    [Writer {worker_id}] Sync error at iteration {i}: {e}")
        time.sleep(0.01)  # Small delay to simulate real-world conditions
    
    print(f"    [Writer {worker_id}] Completed {iterations} iterations")

def worker_reader(shm_name: str, worker_id: int, iterations: int):
    """Worker process that reads from shared memory."""
    gv = GlobalVars(is_logging_enabled=False)
    
    successful_reads = 0
    for i in range(iterations):
        try:
            gv.shm_update(shm_name)
            successful_reads += 1
        except Exception as e:
            print(f"    [Reader {worker_id}] Update error at iteration {i}: {e}")
        time.sleep(0.005)  # Faster read rate
    
    print(f"    [Reader {worker_id}] Completed {successful_reads}/{iterations} successful reads")
    print(f"    [Reader {worker_id}] Final variables count: {len(gv.list_vars().data)}")

def test_race_condition_multiprocess():
    """Test race condition handling with multiple processes."""
    print("\n" + "="*60)
    print("TEST 2: Race Condition Test (Multi-Process)")
    print("="*60)
    
    shm_name = "test_shm_race"
    num_writers = 3
    num_readers = 3
    iterations = 20
    
    # Create shared memory in main process
    gv_main = GlobalVars(is_logging_enabled=False)
    result = gv_main.shm_gen(name=shm_name, size=65536)  # Larger size for multi-process
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

def test_concurrent_set_operations():
    """Test concurrent set operations on GlobalVars."""
    print("\n" + "="*60)
    print("TEST 3: Concurrent Set Operations (Thread-Safe Lock Test)")
    print("="*60)
    
    import threading
    
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
    print(f"[5] Test {'PASSED' if expected_vars == actual_vars else 'FAILED'}")
    
    print("\n" + "-"*60)
    print("TEST 3 COMPLETED")
    print("-"*60)

def test_shm_size_limit():
    """Test shared memory size limit handling."""
    print("\n" + "="*60)
    print("TEST 4: Shared Memory Size Limit Test")
    print("="*60)
    
    gv = GlobalVars(is_logging_enabled=False)
    shm_name = "test_shm_size"
    requested_size = 128  # Requested size
    
    print(f"\n[1] Creating shared memory (requested: {requested_size} bytes)...")
    result = gv.shm_gen(name=shm_name, size=requested_size)
    print(f"    Result: {result.success}")
    
    # Check actual allocated size (OS may round up to page size)
    from multiprocessing import shared_memory as shm_module
    shm_check = shm_module.SharedMemory(name=shm_name)
    actual_size = shm_check.size
    shm_check.close()
    print(f"    Note: OS allocated {actual_size} bytes (page-aligned)")
    
    print("\n[2] Adding massive unique data to exceed page-aligned size...")
    import secrets
    # Generate truly unique random data that can't be compressed
    for i in range(30):
        random_data = secrets.token_hex(512)  # 1KB of unique hex per key
        gv.set(f"unique_key_{i}", random_data, overwrite=True)
    
    import pickle
    serialized_size = len(pickle.dumps(gv._GlobalVars__vars__))
    print(f"    Serialized size: {serialized_size} bytes")
    print(f"    Actual shared memory size: {actual_size} bytes")
    print(f"    Will exceed: {serialized_size > actual_size}")
    
    print("\n[3] Attempting to sync...")
    result = gv.shm_sync(shm_name)
    print(f"    Result success: {result.success}")
    if not result.success:
        print(f"    ✓ Error handled correctly!")
        print(f"    Error type: {result.error}")
    else:
        print("    ✓ Sync succeeded (data fit in allocated space)")
    
    print("\n[4] Cleaning up...")
    gv.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 4 COMPLETED")
    print("-"*60)

# ============================================
# Main Entry Point
# ============================================

def test_concurrent_read_modify_write():
    """Test concurrent read-modify-write operations across 4 processes."""
    print("\n" + "="*60)
    print("TEST 5: Concurrent Read-Modify-Write (4 Processes)")
    print("="*60)
    
    shm_name = "test_shm_rmw"
    num_processes = 4
    iterations_per_process = 50
    expected_final_value = num_processes * iterations_per_process
    
    # Create shared memory and initialize counter
    gv_main = GlobalVars(is_logging_enabled=False)
    gv_main.shm_gen(name=shm_name, size=4096)
    gv_main.set("counter", 0, overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[1] Initial counter value: {gv_main.get('counter').data}")
    print(f"[2] Starting {num_processes} processes, each incrementing {iterations_per_process} times")
    print(f"[3] Expected final value: {expected_final_value}")
    
    # Create and start processes
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = Process(target=worker_increment, args=(shm_name, i, iterations_per_process))
        processes.append(p)
        p.start()
    
    # Wait for all processes
    for p in processes:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    # Check final value
    gv_main.shm_update(shm_name)
    final_value = gv_main.get("counter").data
    
    print(f"\n[4] All processes completed in {elapsed_time:.2f} seconds")
    print(f"[5] Final counter value: {final_value}")
    print(f"[6] Expected value: {expected_final_value}")
    print(f"[7] Lost updates: {expected_final_value - final_value}")
    
    if final_value == expected_final_value:
        print("\n    ✓ TEST PASSED - No data loss!")
    else:
        print(f"\n    ⚠ TEST SHOWS RACE CONDITION - {expected_final_value - final_value} updates lost")
        print("    This is expected behavior without inter-process locking.")
    
    # Cleanup
    gv_main.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 5 COMPLETED")
    print("-"*60)

def test_concurrent_read_modify_write_with_file_lock():
    """Test concurrent read-modify-write with file-based locking."""
    print("\n" + "="*60)
    print("TEST 6: Concurrent R-M-W with File Lock (4 Processes)")
    print("="*60)
    
    import tempfile
    import os
    
    shm_name = "test_shm_rmw_lock"
    num_processes = 4
    iterations_per_process = 50
    expected_final_value = num_processes * iterations_per_process
    
    # Create a lock file
    lock_file_path = os.path.join(tempfile.gettempdir(), "globalvars_test.lock")
    
    # Create shared memory and initialize counter
    gv_main = GlobalVars(is_logging_enabled=False)
    gv_main.shm_gen(name=shm_name, size=4096)
    gv_main.set("counter", 0, overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[1] Initial counter value: {gv_main.get('counter').data}")
    print(f"[2] Starting {num_processes} processes with file-based locking")
    print(f"[3] Expected final value: {expected_final_value}")
    
    # Create and start processes
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = Process(target=worker_increment_with_lock, args=((shm_name, i, iterations_per_process, lock_file_path),))
        processes.append(p)
        p.start()
    
    # Wait for all processes
    for p in processes:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    # Check final value
    gv_main.shm_update(shm_name)
    final_value = gv_main.get("counter").data
    
    print(f"\n[4] All processes completed in {elapsed_time:.2f} seconds")
    print(f"[5] Final counter value: {final_value}")
    print(f"[6] Expected value: {expected_final_value}")
    
    if final_value == expected_final_value:
        print("\n    ✓ TEST PASSED - File lock prevented data loss!")
    else:
        print(f"\n    ✗ TEST FAILED - {expected_final_value - final_value} updates lost")
    
    # Cleanup
    gv_main.shm_close(shm_name)
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)
    
    print("\n" + "-"*60)
    print("TEST 6 COMPLETED")
    print("-"*60)

def test_concurrent_with_shm_lock():
    """Test concurrent R-M-W with shared multiprocessing.Lock."""
    print("\n" + "="*60)
    print("TEST 7: Concurrent R-M-W with shm_gen Lock (4 Processes)")
    print("="*60)
    
    shm_name = "test_shm_lock_ctx"
    num_processes = 4
    iterations_per_process = 50
    expected_final_value = num_processes * iterations_per_process
    
    # Create shared memory with lock
    gv_main = GlobalVars(is_logging_enabled=False)
    result = gv_main.shm_gen(name=shm_name, size=4096, create_lock=True)
    shm_lock = result.data  # Get the shared lock
    
    gv_main.set("counter", 0, overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[1] Initial counter value: {gv_main.get('counter').data}")
    print(f"[2] Starting {num_processes} processes with shared multiprocessing.Lock")
    print(f"[3] Expected final value: {expected_final_value}")
    
    # Create and start processes - pass the lock to each process
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = Process(target=worker_increment_with_shm_lock, args=((shm_name, i, iterations_per_process, shm_lock),))
        processes.append(p)
        p.start()
    
    # Wait for all processes
    for p in processes:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    # Check final value
    gv_main.shm_update(shm_name)
    final_value = gv_main.get("counter").data
    
    print(f"\n[4] All processes completed in {elapsed_time:.2f} seconds")
    print(f"[5] Final counter value: {final_value}")
    print(f"[6] Expected value: {expected_final_value}")
    
    if final_value == expected_final_value:
        print("\n    ✓ TEST PASSED - Shared Lock prevented data loss!")
    else:
        print(f"\n    ✗ TEST FAILED - {expected_final_value - final_value} updates lost")
    
    # Cleanup
    gv_main.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 7 COMPLETED")
    print("-"*60)

def test_concurrent_with_atomic_modify():
    """Test concurrent R-M-W with shm_atomic_modify."""
    print("\n" + "="*60)
    print("TEST 8: Concurrent R-M-W with shm_atomic_modify (4 Processes)")
    print("="*60)
    
    shm_name = "test_shm_atomic"
    num_processes = 4
    iterations_per_process = 50
    expected_final_value = num_processes * iterations_per_process
    
    # Create shared memory and initialize counter
    gv_main = GlobalVars(is_logging_enabled=False)
    gv_main.shm_gen(name=shm_name, size=4096)
    gv_main.set("counter", 0, overwrite=True)
    gv_main.shm_sync(shm_name)
    
    print(f"\n[1] Initial counter value: {gv_main.get('counter').data}")
    print(f"[2] Starting {num_processes} processes with shm_atomic_modify")
    print(f"[3] Expected final value: {expected_final_value}")
    
    # Create and start processes
    processes = []
    start_time = time.time()
    
    for i in range(num_processes):
        p = Process(target=worker_increment_atomic, args=((shm_name, i, iterations_per_process),))
        processes.append(p)
        p.start()
    
    # Wait for all processes
    for p in processes:
        p.join()
    
    elapsed_time = time.time() - start_time
    
    # Check final value
    gv_main.shm_update(shm_name)
    final_value = gv_main.get("counter").data
    
    print(f"\n[4] All processes completed in {elapsed_time:.2f} seconds")
    print(f"[5] Final counter value: {final_value}")
    print(f"[6] Expected value: {expected_final_value}")
    
    if final_value == expected_final_value:
        print("\n    ✓ TEST PASSED - shm_atomic_modify prevented data loss!")
    else:
        print(f"\n    ✗ TEST FAILED - {expected_final_value - final_value} updates lost")
    
    # Cleanup
    gv_main.shm_close(shm_name)
    
    print("\n" + "-"*60)
    print("TEST 8 COMPLETED")
    print("-"*60)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("GLOBALVARS SHARED MEMORY TEST SUITE")
    print("="*60)
    
    # Run tests
    test_basic_shm_operations()
    test_race_condition_multiprocess()
    test_concurrent_set_operations()
    test_shm_size_limit()
    test_concurrent_read_modify_write()
    test_concurrent_read_modify_write_with_file_lock()
    test_concurrent_with_shm_lock()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60 + "\n")
