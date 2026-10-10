import sys
import time
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from dev_tools import start_server, stop_server, RUNNING_SERVERS

def run_lifecycle_test():
    print("--- Phase 2.2 Lifecycle Test ---")
    
    # 1. Start the configured server
    print("\n1. Starting server...")
    result1 = start_server("ai assistant", "python")
    print(f"Result: {result1}")
    
    # 2. Check its status
    print("\n2. Checking status...")
    server_key = "ai assistant_python"
    is_running = server_key in RUNNING_SERVERS and RUNNING_SERVERS[server_key].poll() is None
    print(f"Is running: {is_running}")
    if is_running:
        print(f"PID: {RUNNING_SERVERS[server_key].pid}")
        
    # 3. Attempt a duplicate start
    print("\n3. Attempting duplicate start...")
    result3 = start_server("ai assistant", "python")
    print(f"Result: {result3}")
    
    # Let it run for just a second so it spawns fully
    time.sleep(1)
    
    # 4. Stop the tracked server
    print("\n4. Stopping server...")
    result4 = stop_server("ai assistant", "python")
    print(f"Result: {result4}")
    
    # 5. Check its status again
    print("\n5. Checking status after stop...")
    is_running_after = server_key in RUNNING_SERVERS
    print(f"Is running: {is_running_after}")

if __name__ == "__main__":
    run_lifecycle_test()
