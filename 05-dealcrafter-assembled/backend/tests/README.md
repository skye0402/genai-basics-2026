# Backend Tests

This folder contains all backend testing files and test results.

## Test Files

### Unit Tests
- **`run_tests.py`** - Automated unit test runner
  - Tests imports and module structure
  - Tests mock service functionality
  - Outputs: `test_results.txt`

### Integration Tests
- **`test_http.py`** - HTTP endpoint testing
  - Tests all API endpoints
  - Tests SSE streaming
  - Outputs: `http_test_results.txt`

### Shell Tests
- **`test_api.sh`** - Bash script for API testing
  - Quick curl-based endpoint tests
  - Outputs: `backend.log`

## Running Tests

### Run Unit Tests
```bash
cd backend
uv run python tests/run_tests.py
```

### Run HTTP Tests
```bash
cd backend
python3 tests/test_http.py
```

### Run Shell Tests
```bash
cd backend/tests
chmod +x test_api.sh
./test_api.sh
```

## Test Results

All test results are saved in this `tests/` folder:
- `test_results.txt` - Unit test output
- `http_test_results.txt` - HTTP test output
- `backend.log` - Server logs from shell tests
- `TEST-REPORT.md` - Comprehensive test report

## Requirements

- Python 3.12+
- uv package manager
- requests library (for HTTP tests)
- curl (for shell tests)

## Test Coverage

✅ Import validation  
✅ Configuration loading  
✅ Route registration  
✅ Mock service responses  
✅ SSE streaming format  
✅ HTTP endpoints  
✅ CORS configuration  
✅ Error handling  
