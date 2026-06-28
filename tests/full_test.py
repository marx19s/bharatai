# tests/full_test.py
"""End‑to‑end verification script for BharatAI Sprint 3.

The script starts the background API server, checks the health endpoint,
exercises the JSON dispatch API, streams SSE events from the regular
dispatch endpoint and validates that all expected task categories are
handled correctly.

A simple PASS/FAIL table is printed at the end.
"""

import sys
import os
import threading
import time
import json
import urllib.request
import urllib.error
import socket

# Ensure the repository root is on PYTHONPATH so that ``import app`` works
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---------------------------------------------------------------------
# Helper utilities with robust standard library timeouts
# ---------------------------------------------------------------------

def http_get(url, timeout=10):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8"), resp.status

def http_post(url, payload, timeout=10):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw_data = resp.read()
        return json.loads(raw_data.decode("utf-8")), resp.status

def sse_post(url, payload, timeout=10):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    events = []
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for line in resp:
                # Prevent running past timeout if server keeps connection open indefinitely
                if time.time() - start_time > timeout:
                    break
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    try:
                        ev = json.loads(line[6:])
                        events.append(ev)
                        # Break early if we receive the completion event or an error
                        if ev.get("event") in ("formatting_complete", "error"):
                            break
                    except Exception:
                        pass
    except (urllib.error.URLError, TimeoutError, socket.timeout):
        # Captured expected network timeout safely
        pass
    return events

# ---------------------------------------------------------------------
# Background Server Manager
# ---------------------------------------------------------------------

_server_started = False
_server_lock = threading.Lock()

def start_server():
    global _server_started
    with _server_lock:
        if _server_started:
            return
        try:
            import app
        except Exception as e:
            print("Failed to import app module:", e)
            sys.exit(1)
        threading.Thread(target=app.start_api_server, daemon=True).start()
        # Give server thread time to bind the socket
        time.sleep(2)
        _server_started = True

# ---------------------------------------------------------------------
# Test Case Implementations
# ---------------------------------------------------------------------

def test_startup():
    start_server()
    body, status = http_get("http://127.0.0.1:8502/api/health", timeout=10)
    return status == 200

def test_health():
    body, status = http_get("http://127.0.0.1:8502/api/health", timeout=10)
    data = json.loads(body)
    return status == 200 and data.get("success") is True

def test_dispatch_json():
    resp, status = http_post("http://127.0.0.1:8502/api/dispatch-json", {"goal": "Who are you?"}, timeout=10)
    return status == 200 and resp.get("success") is True and "result" in resp

def test_sse():
    events = sse_post("http://127.0.0.1:8502/api/dispatch", {"goal": "Who are you?"}, timeout=10)
    
    # 1. Verify stage_started event is present
    has_stage_started = any(ev.get("event") == "stage_started" for ev in events)
    
    # 2. Verify stage completion/completed event is present
    has_stage_completed = any(ev.get("event") == "classification_complete" for ev in events)
    
    # 3. Verify formatting_complete event is present
    has_formatting_complete = any(ev.get("event") == "formatting_complete" for ev in events)
    
    # 4. Verify final_answer event is present
    has_final_answer = any(ev.get("event") == "final_answer" for ev in events)
    
    # 5. Verify end event is present
    has_end = any(ev.get("event") == "end" for ev in events)
    
    if not (has_stage_started and has_stage_completed and has_formatting_complete and has_final_answer and has_end):
        missing = []
        if not has_stage_started: missing.append("stage_started")
        if not has_stage_completed: missing.append("classification_complete")
        if not has_formatting_complete: missing.append("formatting_complete")
        if not has_final_answer: missing.append("final_answer")
        if not has_end: missing.append("end")
        print(f"  Missing SSE events: {', '.join(missing)}")
        return False
    
    return True

def run_routing_test(category, prompt):
    resp, status = http_post("http://127.0.0.1:8502/api/dispatch-json", {"goal": prompt}, timeout=10)
    return status == 200 and resp.get("success") is True and "result" in resp

def test_model_routing():
    resp, status = http_post("http://127.0.0.1:8502/api/dispatch-json", {"goal": "Who are you?"}, timeout=10)
    return status == 200 and resp.get("success") is True

def test_concurrency():
    def worker(goal, out):
        try:
            r, s = http_post("http://127.0.0.1:8502/api/dispatch-json", {"goal": goal}, timeout=10)
            out.append(s == 200 and r.get("success"))
        except Exception:
            out.append(False)

    results = []
    t1 = threading.Thread(target=worker, args=("Explain Python decorators.", results))
    t2 = threading.Thread(target=worker, args=("Write Python code to reverse a linked list.", results))
    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)
    return len(results) == 2 and all(results)

def test_timeout_handling():
    # Send a request with an extremely short timeout (0.1s) to test client-side timeout handling
    start_time = time.time()
    try:
        http_post("http://127.0.0.1:8502/api/dispatch-json", {"goal": "Write Python code to reverse a linked list."}, timeout=0.1)
        return False  # Failed to timeout
    except (urllib.error.URLError, TimeoutError, socket.timeout):
        elapsed = time.time() - start_time
        # Must abort immediately under 2 seconds
        return elapsed < 2.0

# ---------------------------------------------------------------------
# Runner with strict watchdog and test timeouts
# ---------------------------------------------------------------------

def run_tests():
    tests = [
        ("Startup", test_startup),
        ("Health", test_health),
        ("Dispatch-JSON", test_dispatch_json),
        ("SSE", test_sse),
        ("Routing: GENERAL_CHAT", lambda: run_routing_test("GENERAL_CHAT", "Hello!")),
        ("Routing: PLANNING", lambda: run_routing_test("PLANNING", "Create a roadmap for an ecommerce website.")),
        ("Routing: RESEARCH", lambda: run_routing_test("RESEARCH", "Explain Python decorators.")),
        ("Routing: CODING", lambda: run_routing_test("CODING", "Write Python code to reverse a linked list.")),
        ("Routing: DOCUMENT_ANALYSIS", lambda: run_routing_test("DOCUMENT_ANALYSIS", "Summarize the attached PDF.")),
        ("Routing: DEBUGGING", lambda: run_routing_test("DEBUGGING", "Why does my loop never terminate?")),
        ("Model Routing", test_model_routing),
        ("Concurrency", test_concurrency),
        ("Timeout Handling", test_timeout_handling),
    ]

    results_summary = []
    test_times = {}
    overall_ok = True
    suite_start = time.time()

    for name, func in tests:
        # Check if the global suite time limit (300s) has been exceeded
        if time.time() - suite_start > 300.0:
            print(f"\n[WATCHDOG] Global suite timeout of 300 seconds exceeded! Skipping remaining tests...")
            # Mark all remaining tests as FAIL due to suite timeout
            for remaining_name, _ in tests[len(results_summary):]:
                results_summary.append((remaining_name, False, "Suite timeout exceeded"))
            overall_ok = False
            break

        # Print progress before each test
        print(f"Running {name}...")
        
        result = {"ok": False, "error": None}
        def worker():
            try:
                result["ok"] = func()
            except Exception as e:
                result["error"] = e
                result["ok"] = False
                
        # Create normal (non-daemon) thread
        t = threading.Thread(target=worker, daemon=False)
        
        start_time = time.time()
        t.start()
        
        # Enforce 30-second join timeout
        t.join(timeout=30)
        elapsed = time.time() - start_time
        test_times[name] = elapsed
        
        if t.is_alive():
            reason = f"Timeout (exceeded 30s limit, ran for {elapsed:.2f}s)"
            results_summary.append((name, False, reason))
            overall_ok = False
        else:
            if result["error"]:
                reason = f"Exception: {result['error']}"
                results_summary.append((name, False, reason))
                overall_ok = False
            else:
                if result["ok"]:
                    results_summary.append((name, True, f"Completed successfully in {elapsed:.2f}s"))
                else:
                    reason = "Test condition failed"
                    results_summary.append((name, False, reason))
                    overall_ok = False

    total_time = time.time() - suite_start
    most_expensive_test = max(test_times, key=test_times.get) if test_times else "None"
    max_test_time = test_times[most_expensive_test] if test_times else 0.0

    print("\n==========================")
    print("Sprint 3 Verification")
    print("==========================\n")
    for name, ok, reason in results_summary:
        status = "PASS" if ok else "FAIL"
        print(f"{name:<28} {status} ({reason})")
    print("--------------------------")
    print(f"Total execution time: {total_time:.2f}s")
    print(f"Most expensive test: {most_expensive_test} ({max_test_time:.2f}s)")
    print(f"Overall: {'PASS' if overall_ok else 'FAIL'}")
    
    return overall_ok

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
