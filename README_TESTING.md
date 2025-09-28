# Testing Guide for Billions Bounty Web Interface

This guide covers all the testing infrastructure for the Billions Bounty web interface, including frontend components, backend APIs, integration tests, and end-to-end tests.

## 🧪 Test Structure

### Frontend Tests (React/Next.js)
- **Location**: `frontend/src/__tests__/`
- **Framework**: Jest + React Testing Library
- **Coverage**: Component unit tests, user interactions, API mocking

### Backend Tests (FastAPI)
- **Location**: `tests/`
- **Framework**: pytest + httpx
- **Coverage**: API endpoints, business logic, database operations

### Integration Tests
- **Location**: `tests/test_integration.py`
- **Framework**: pytest + httpx
- **Coverage**: Frontend-backend communication, data flow

### End-to-End Tests
- **Location**: `frontend/e2e/`
- **Framework**: Playwright
- **Coverage**: Full user workflows, browser interactions

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

### 2. Run All Tests

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type backend
python run_tests.py --type frontend
python run_tests.py --type e2e
```

### 3. Quick Interface Test

```bash
# Test if web interface is working (requires services running)
python test_web_interface.py
```

## 📋 Test Categories

### Frontend Component Tests

#### ChatInterface Tests
- ✅ Renders correctly with all elements
- ✅ Handles wallet connection states
- ✅ Manages message input and submission
- ✅ Displays user and AI messages
- ✅ Shows winner/blacklisted message styling
- ✅ Handles API errors gracefully
- ✅ Shows loading states
- ✅ Fetches bounty status

#### bountyDisplay Tests
- ✅ Shows loading and error states
- ✅ Displays bounty statistics correctly
- ✅ Shows next rollover information
- ✅ Displays user history when connected
- ✅ Shows recent winners
- ✅ Displays how-to-play instructions
- ✅ Updates data every 5 seconds
- ✅ Formats currency and percentages correctly

#### AdminDashboard Tests
- ✅ Displays admin statistics
- ✅ Shows blacklisted phrases list
- ✅ Allows adding new phrases
- ✅ Prevents empty phrase submission
- ✅ Toggles phrase status
- ✅ Shows system status information
- ✅ Handles API errors gracefully
- ✅ Shows loading states

#### PaymentFlow Tests
- ✅ Displays payment elements correctly
- ✅ Handles payment method selection
- ✅ Manages amount selection
- ✅ Fetches and displays quotes
- ✅ Creates payments when wallet connected
- ✅ Shows processing states
- ✅ Handles success/failure states
- ✅ Polls payment status
- ✅ Handles timeouts
- ✅ Validates input constraints

### Backend API Tests

#### Core Endpoints
- ✅ Root endpoint (`/`)
- ✅ Chat interface HTML (`/chat`)
- ✅ Chat API (`/api/chat`)
- ✅ Prize pool status (`/api/prize-pool`)
- ✅ Platform stats (`/api/stats`)

#### Wallet Integration
- ✅ Wallet connection (`/api/wallet/connect`)
- ✅ Wallet balance (`/api/wallet/balance/{address}`)
- ✅ Wallet balances (`/api/wallet/balances/{address}`)

#### Payment System
- ✅ Payment options (`/api/payment/options`)
- ✅ Payment creation (`/api/payment/create`)
- ✅ Payment verification (`/api/payment/verify`)
- ✅ Payment rates (`/api/payment/rates`)

#### Admin Features
- ✅ Blacklist management (`/api/admin/blacklist`)
- ✅ Admin statistics (`/api/admin/stats`)

### Integration Tests

#### Frontend-Backend Communication
- ✅ Chat flow integration
- ✅ bounty data flow
- ✅ Wallet connection flow
- ✅ Payment flow integration
- ✅ Admin dashboard integration
- ✅ Error handling integration

#### Data Flow Tests
- ✅ Chat message flow
- ✅ bounty data flow
- ✅ Wallet connection flow

### End-to-End Tests

#### Chat Interface E2E
- ✅ Component rendering
- ✅ Wallet connection states
- ✅ Message submission
- ✅ Winner/blacklisted styling
- ✅ Error handling
- ✅ Loading states
- ✅ bounty status fetching

#### bounty Display E2E
- ✅ Statistics display
- ✅ Rollover information
- ✅ User history
- ✅ Recent winners
- ✅ How-to-play instructions
- ✅ Data updates
- ✅ Currency formatting

#### Admin Dashboard E2E
- ✅ Statistics display
- ✅ Blacklist management
- ✅ Phrase addition
- ✅ Status toggling
- ✅ System status
- ✅ Error handling

#### Payment Flow E2E
- ✅ Payment method selection
- ✅ Amount selection
- ✅ Quote fetching
- ✅ Payment creation
- ✅ Status polling
- ✅ Success/failure handling

## 🛠️ Test Configuration

### Jest Configuration
- **File**: `frontend/jest.config.js`
- **Setup**: `frontend/jest.setup.js`
- **Coverage**: 70% threshold
- **Environment**: jsdom

### Playwright Configuration
- **File**: `frontend/playwright.config.ts`
- **Browsers**: Chrome, Firefox, Safari, Mobile
- **Base URL**: `http://localhost:3000`
- **Auto-start**: Development server

### Pytest Configuration
- **Async support**: pytest-asyncio
- **HTTP client**: httpx
- **Mocking**: unittest.mock
- **Coverage**: pytest-cov

## 📊 Coverage Reports

### Frontend Coverage
```bash
cd frontend
npm run test:coverage
```
- Generates coverage report in `frontend/coverage/`
- HTML report available at `frontend/coverage/lcov-report/index.html`

### Backend Coverage
```bash
pytest --cov=src tests/
```
- Generates coverage report in `htmlcov/`
- Shows coverage for all source files

## 🔧 Test Scripts

### Main Test Runner
```bash
# Run all tests
python run_tests.py

# Run specific types
python run_tests.py --type backend
python run_tests.py --type frontend
python run_tests.py --type e2e

# Check dependencies only
python run_tests.py --check-deps
```

### Individual Test Commands

#### Frontend Tests
```bash
cd frontend

# Run tests once
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

#### Backend Tests
```bash
# Run all backend tests
pytest tests/

# Run specific test file
pytest tests/test_web_api.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

## 🚨 Troubleshooting

### Common Issues

#### Frontend Tests Failing
1. **Dependencies not installed**
   ```bash
   cd frontend
   npm install
   ```

2. **Jest configuration issues**
   - Check `frontend/jest.config.js`
   - Verify `frontend/jest.setup.js` exists

3. **Mock issues**
   - Check wallet adapter mocks in `jest.setup.js`
   - Verify fetch mocking

#### Backend Tests Failing
1. **Dependencies not installed**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio httpx
   ```

2. **Database issues**
   - Check database connection
   - Verify test database setup

3. **Import errors**
   - Check Python path
   - Verify module structure

#### E2E Tests Failing
1. **Browsers not installed**
   ```bash
   cd frontend
   npx playwright install
   ```

2. **Services not running**
   - Start backend: `python main.py`
   - Start frontend: `cd frontend && npm run dev`

3. **Port conflicts**
   - Check if ports 3000 and 8000 are available
   - Update configuration if needed

### Debug Mode

#### Frontend Debug
```bash
cd frontend
npm test -- --verbose
```

#### Backend Debug
```bash
pytest -v -s tests/
```

#### E2E Debug
```bash
cd frontend
npx playwright test --debug
```

## 📈 Continuous Integration

### GitHub Actions
- **File**: `.github/workflows/test.yml`
- **Triggers**: Push to main/develop, PRs
- **Jobs**: Backend, Frontend, E2E, Integration
- **Artifacts**: Test results, coverage reports

### Local CI Simulation
```bash
# Run all tests as CI would
python run_tests.py
```

## 🎯 Best Practices

### Writing Tests
1. **Test one thing at a time**
2. **Use descriptive test names**
3. **Mock external dependencies**
4. **Test both success and failure cases**
5. **Keep tests independent**

### Test Data
1. **Use consistent test data**
2. **Clean up after tests**
3. **Use factories for complex data**
4. **Mock time-dependent operations**

### Performance
1. **Run tests in parallel when possible**
2. **Use appropriate timeouts**
3. **Mock slow operations**
4. **Clean up resources**

## 📚 Additional Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain coverage thresholds
4. Update this documentation
5. Add E2E tests for user workflows

## 📞 Support

If you encounter issues with testing:
1. Check this guide first
2. Review test output carefully
3. Check service availability
4. Verify dependencies
5. Create an issue with details
