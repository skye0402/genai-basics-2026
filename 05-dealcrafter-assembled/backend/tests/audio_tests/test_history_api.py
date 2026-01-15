"""
Simple test script for chat history API endpoints.
Run with: python test_history_api.py
Make sure the backend server is running on http://localhost:8000
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"


def test_create_session():
    """Test creating a new session."""
    print("\n=== Test: Create Session ===")
    response = requests.post(f"{BASE_URL}/chat-history", json={"title": "Test Chat"})
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data.get("session_id")


def test_list_sessions():
    """Test listing all sessions."""
    print("\n=== Test: List Sessions ===")
    response = requests.get(f"{BASE_URL}/chat-history")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data


def test_get_session(session_id):
    """Test getting a specific session."""
    print(f"\n=== Test: Get Session {session_id} ===")
    response = requests.get(f"{BASE_URL}/chat-history/{session_id}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, default=str)}")
    return data


def test_generate_title(session_id):
    """Test generating a title for a session."""
    print(f"\n=== Test: Generate Title for {session_id} ===")
    response = requests.post(
        f"{BASE_URL}/generate-title",
        json={
            "session_id": session_id,
            "messages": []
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data


def test_delete_session(session_id):
    """Test deleting a session."""
    print(f"\n=== Test: Delete Session {session_id} ===")
    response = requests.delete(f"{BASE_URL}/chat-history/{session_id}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return data


def main():
    """Run all tests."""
    print("=" * 60)
    print("Chat History API Tests")
    print("=" * 60)
    
    try:
        # Test 1: Create a session
        session_id = test_create_session()
        
        # Test 2: List sessions
        test_list_sessions()
        
        # Test 3: Get specific session
        test_get_session(session_id)
        
        # Test 4: Generate title
        test_generate_title(session_id)
        
        # Test 5: Get session again to see updated title
        test_get_session(session_id)
        
        # Test 6: Create another session
        session_id2 = test_create_session()
        
        # Test 7: List all sessions
        test_list_sessions()
        
        # Test 8: Delete first session
        test_delete_session(session_id)
        
        # Test 9: List sessions after deletion
        test_list_sessions()
        
        # Test 10: Try to get deleted session (should fail)
        print(f"\n=== Test: Get Deleted Session (should fail) ===")
        response = requests.get(f"{BASE_URL}/chat-history/{session_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 404:
            print("✓ Correctly returned 404")
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server.")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
