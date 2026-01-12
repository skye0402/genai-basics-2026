"""Simple test runner that writes to file."""
import asyncio
import sys


async def test_mock_service():
    """Test mock service."""
    from app.services.mock_service import generate_mock_response
    
    results = []
    results.append("=" * 60)
    results.append("Testing Mock Service")
    results.append("=" * 60)
    
    # Test product request
    results.append("\nTest 1: Product request")
    count = 0
    async for event in generate_mock_response("show me products"):
        count += 1
        results.append(f"  Event {count}: {event['event']}")
    results.append(f"  Total events: {count}")
    
    # Test sales request
    results.append("\nTest 2: Sales request")
    count = 0
    async for event in generate_mock_response("show me sales"):
        count += 1
        results.append(f"  Event {count}: {event['event']}")
    results.append(f"  Total events: {count}")
    
    # Test default
    results.append("\nTest 3: Default request")
    count = 0
    async for event in generate_mock_response("hello"):
        count += 1
        results.append(f"  Event {count}: {event['event']}")
    results.append(f"  Total events: {count}")
    
    return results


def test_imports():
    """Test imports."""
    results = []
    results.append("=" * 60)
    results.append("Testing Imports")
    results.append("=" * 60)
    
    try:
        from app.main import app
        results.append("✓ app.main")
        
        from app.core.config import settings
        results.append(f"✓ app.core.config (mock_mode={settings.mock_mode})")
        
        from app.models.schemas import ChatRequest
        results.append("✓ app.models.schemas")
        
        from app.api.chat import router
        results.append("✓ app.api.chat")
        
        # Check routes
        routes = [r.path for r in app.routes]
        results.append(f"\nRoutes ({len(routes)}):")
        for route in sorted(routes):
            results.append(f"  - {route}")
        
        results.append("\n✅ All imports successful!")
        
    except Exception as e:
        results.append(f"\n❌ Import failed: {e}")
        import traceback
        results.append(traceback.format_exc())
    
    return results


async def main():
    """Run tests and write to file."""
    all_results = []
    
    all_results.append("BACKEND TEST RESULTS")
    all_results.append("=" * 60)
    all_results.append("")
    
    # Test imports
    all_results.extend(test_imports())
    all_results.append("")
    
    # Test mock service
    all_results.extend(await test_mock_service())
    all_results.append("")
    
    all_results.append("=" * 60)
    all_results.append("✅ TESTS COMPLETE")
    all_results.append("=" * 60)
    
    # Write to file in tests folder
    output = "\n".join(all_results)
    import os
    test_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(test_dir, "test_results.txt")
    
    with open(output_file, "w") as f:
        f.write(output)
    
    print(output)
    print(f"\n📄 Results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
