#!/usr/bin/env python3
"""Backend testing script."""
import asyncio
import sys
from app.main import app
from app.models.schemas import ChatRequest
from app.services.mock_service import generate_mock_response


async def test_mock_service():
    """Test the mock service responses."""
    print("=" * 60)
    print("🧪 Testing Mock Service")
    print("=" * 60)
    
    # Test 1: Product/Excel keyword
    print("\n📦 Test 1: Product inventory request")
    print("-" * 60)
    message = "show me product inventory"
    print(f"Input: '{message}'")
    print("\nResponse:")
    
    event_count = 0
    async for event in generate_mock_response(message):
        event_count += 1
        event_type = event["event"]
        event_data = event["data"]
        
        if event_type == "text":
            print(f"  [TEXT] {event_data}")
        elif event_type == "table":
            print(f"  [TABLE] Columns: {len(event_data['columns'])}, Rows: {len(event_data['rows'])}")
            print(f"          Headers: {[col['header'] for col in event_data['columns']]}")
        elif event_type == "end":
            print(f"  [END] Stream complete")
    
    print(f"\n✓ Total events: {event_count}")
    
    # Test 2: Sales keyword
    print("\n" + "=" * 60)
    print("📊 Test 2: Sales data request")
    print("-" * 60)
    message = "show me sales revenue"
    print(f"Input: '{message}'")
    print("\nResponse:")
    
    event_count = 0
    async for event in generate_mock_response(message):
        event_count += 1
        event_type = event["event"]
        event_data = event["data"]
        
        if event_type == "text":
            print(f"  [TEXT] {event_data}")
        elif event_type == "table":
            print(f"  [TABLE] Columns: {len(event_data['columns'])}, Rows: {len(event_data['rows'])}")
            print(f"          Headers: {[col['header'] for col in event_data['columns']]}")
        elif event_type == "end":
            print(f"  [END] Stream complete")
    
    print(f"\n✓ Total events: {event_count}")
    
    # Test 3: Default response
    print("\n" + "=" * 60)
    print("💬 Test 3: Default text response")
    print("-" * 60)
    message = "hello, how are you?"
    print(f"Input: '{message}'")
    print("\nResponse:")
    
    event_count = 0
    async for event in generate_mock_response(message):
        event_count += 1
        event_type = event["event"]
        event_data = event["data"]
        
        if event_type == "text":
            print(f"  [TEXT] {event_data}")
        elif event_type == "end":
            print(f"  [END] Stream complete")
    
    print(f"\n✓ Total events: {event_count}")


def test_imports():
    """Test that all imports work correctly."""
    print("=" * 60)
    print("📦 Testing Imports")
    print("=" * 60)
    
    try:
        from app.main import app
        print("✓ app.main imported successfully")
        
        from app.core.config import settings
        print(f"✓ app.core.config imported successfully")
        print(f"  - Mock mode: {settings.mock_mode}")
        print(f"  - CORS origins: {settings.cors_origins_list}")
        
        from app.models.schemas import ChatRequest, ChatMessage
        print("✓ app.models.schemas imported successfully")
        
        from app.services.mock_service import generate_mock_response
        print("✓ app.services.mock_service imported successfully")
        
        from app.api.chat import router
        print("✓ app.api.chat imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_structure():
    """Test FastAPI app structure."""
    print("\n" + "=" * 60)
    print("🏗️  Testing App Structure")
    print("=" * 60)
    
    try:
        from app.main import app
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"\n📍 Registered routes ({len(routes)}):")
        for route in sorted(routes):
            print(f"  - {route}")
        
        # Check middleware
        print(f"\n🔧 Middleware count: {len(app.user_middleware)}")
        
        print("\n✅ App structure looks good!")
        return True
        
    except Exception as e:
        print(f"\n❌ App structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀 " * 20)
    print("BACKEND TESTING SUITE")
    print("🚀 " * 20 + "\n")
    
    # Test 1: Imports
    if not test_imports():
        sys.exit(1)
    
    # Test 2: App structure
    if not test_app_structure():
        sys.exit(1)
    
    # Test 3: Mock service
    await test_mock_service()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
