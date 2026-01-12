"""HTTP endpoint testing."""
import subprocess
import time
import requests
import json
import sys
import os


def start_server():
    """Start the backend server."""
    print("🚀 Starting backend server...")
    # Get backend directory (parent of tests folder)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(4)  # Wait for server to start
    return proc


def test_endpoints():
    """Test HTTP endpoints."""
    results = []
    results.append("=" * 60)
    results.append("HTTP ENDPOINT TESTING")
    results.append("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Root endpoint
    results.append("\n📍 Test 1: GET /")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        results.append(f"  Status: {response.status_code}")
        results.append(f"  Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        results.append("  ✅ PASSED")
    except Exception as e:
        results.append(f"  ❌ FAILED: {e}")
    
    # Test 2: Health endpoint
    results.append("\n📍 Test 2: GET /health")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        results.append(f"  Status: {response.status_code}")
        results.append(f"  Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        results.append("  ✅ PASSED")
    except Exception as e:
        results.append(f"  ❌ FAILED: {e}")
    
    # Test 3: Chat stream - Product
    results.append("\n📍 Test 3: POST /api/chat-stream (product)")
    try:
        response = requests.post(
            f"{base_url}/api/chat-stream",
            json={"message": "show me products"},
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=10
        )
        results.append(f"  Status: {response.status_code}")
        results.append(f"  Content-Type: {response.headers.get('content-type')}")
        
        # Read SSE events
        events = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                events.append(line)
                if len(events) <= 10:  # Show first 10 lines
                    results.append(f"    {line}")
        
        results.append(f"  Total lines: {len(events)}")
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        results.append("  ✅ PASSED")
    except Exception as e:
        results.append(f"  ❌ FAILED: {e}")
    
    # Test 4: Chat stream - Sales
    results.append("\n📍 Test 4: POST /api/chat-stream (sales)")
    try:
        response = requests.post(
            f"{base_url}/api/chat-stream",
            json={"message": "show me sales data"},
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=10
        )
        results.append(f"  Status: {response.status_code}")
        
        # Count events
        event_types = []
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
                event_types.append(event_type)
        
        results.append(f"  Events: {event_types}")
        assert "table" in event_types
        assert "end" in event_types
        results.append("  ✅ PASSED")
    except Exception as e:
        results.append(f"  ❌ FAILED: {e}")
    
    # Test 5: Chat stream - Default
    results.append("\n📍 Test 5: POST /api/chat-stream (default)")
    try:
        response = requests.post(
            f"{base_url}/api/chat-stream",
            json={"message": "hello"},
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=10
        )
        results.append(f"  Status: {response.status_code}")
        
        # Count events
        event_types = []
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
                event_types.append(event_type)
        
        results.append(f"  Events: {event_types}")
        assert "text" in event_types
        assert "end" in event_types
        results.append("  ✅ PASSED")
    except Exception as e:
        results.append(f"  ❌ FAILED: {e}")
    
    return results


def main():
    """Run HTTP tests."""
    proc = None
    try:
        proc = start_server()
        
        results = test_endpoints()
        
        results.append("\n" + "=" * 60)
        results.append("✅ HTTP TESTING COMPLETE")
        results.append("=" * 60)
        
        output = "\n".join(results)
        
        # Write to file in tests folder
        test_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(test_dir, "http_test_results.txt")
        
        with open(output_file, "w") as f:
            f.write(output)
        
        print(output)
        print(f"\n📄 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if proc:
            print("\n🧹 Stopping server...")
            proc.terminate()
            proc.wait(timeout=5)


if __name__ == "__main__":
    main()
