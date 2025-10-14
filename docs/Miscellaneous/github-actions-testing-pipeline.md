# GitHub Actions Testing Pipeline

## Overview
This document describes the automated testing pipeline implemented for the GupShup Cafe project using GitHub Actions.

## Workflow File
- **Location**: `.github/workflows/test.yml`
- **Name**: Run Tests
- **Purpose**: Automatically run all tests (client and server) on code changes

## Trigger Events
The testing workflow runs automatically on:
- **Push events** to `main` and `develop` branches
- **Pull request events** targeting `main` and `develop` branches

## Workflow Steps

### 1. Environment Setup
- **OS**: Ubuntu Latest
- **Node.js**: Version 18 (with npm cache)
- **Python**: Version 3.12 (with pip cache)

### 2. Dependency Installation
The workflow installs dependencies in this order:
1. Root dependencies (`npm install`)
2. Client dependencies (`cd client && npm install`)
3. Python dependencies (requirements.txt + test dependencies)

### 3. Test Execution
Runs the command: `npm run test:all`

This command executes:
- **Client tests**: Vitest test suite in CI mode
- **Server tests**: Pytest test suite with verbose output

## Environment Variables
- `CI=true`: Set during test execution to ensure vitest runs in CI mode (non-interactive)

## Test Scripts Reference

From root `package.json`:
```json
{
  "test:client": "cd client && vitest",
  "test:server:py": "cd server_py && pytest tests/ -v",
  "test:all": "cd client && vitest && cd ../server_py && pytest tests/ -v"
}
```

## CI Behavior
- **Vitest**: Automatically detects CI environment and runs in non-watch mode
- **Pytest**: Runs with verbose output (`-v` flag)
- **Failure Handling**: If either test suite fails, the workflow will fail

## Viewing Test Results
1. Navigate to the **Actions** tab in the GitHub repository
2. Select the workflow run you want to inspect
3. Click on the **test** job to see detailed logs
4. Each step shows its output, including test results and any failures

## Local Testing
To replicate the CI environment locally:
```bash
# Install all dependencies
npm run install:all

# Run all tests with CI environment
CI=true npm run test:all
```

## Maintenance Notes
- The workflow uses the latest versions of GitHub Actions (v4 for checkout/setup-node, v5 for setup-python)
- Caching is enabled for both npm and pip to speed up workflow execution
- Python test dependencies are explicitly installed to ensure pytest and related packages are available

## Future Enhancements
Potential improvements to consider:
- Add code coverage reporting
- Separate client and server tests into parallel jobs for faster execution
- Add linting checks as a separate job
- Configure test result artifacts for easier debugging
- Add badges to README showing test status
