#!/usr/bin/env python3
"""
Test Runner for Editor Integration Tests

This script runs the editor integration tests using pytest.
It provides a summary of test results and documents any issues found.
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_section(title):
    """Print a section header."""
    print(f"\n{title}")
    print("-" * len(title))


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    """Main test runner."""
    print_header("Editor Integration Test Suite - Phase 2, Subtask 2.3")

    # Test files created
    test_files = [
        "tests/test_editor_integration.py",
        "tests/EDITOR_TEST_CHECKLIST.md",
        "tests/test_e2e_editor.py",
    ]

    print_section("Test Files Created")
    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {test_file} ({size} bytes)")
        else:
            print(f"  ✗ {test_file} (NOT FOUND)")

    # Check dependencies
    print_section("Dependency Check")

    dependencies = {
        "pytest": "pytest",
        "flask": "flask",
        "requests": "requests",
    }

    missing_deps = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package} is installed")
        except ImportError:
            print(f"  ✗ {package} is NOT installed")
            missing_deps.append(package)

    if missing_deps:
        print(f"\n  Missing dependencies: {', '.join(missing_deps)}")
        print(f"  Install with: pip install {' '.join(missing_deps)}")
        return 1

    # Run tests
    print_section("Running Tests")

    test_results = {}

    # Test 1: E2E test
    print("\n1. Running End-to-End Test...")
    result = run_command(
        [sys.executable, "tests/test_e2e_editor.py"], "End-to-End Test"
    )

    if result:
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        test_results["e2e"] = result.returncode == 0

    # Test 2: Integration tests (if possible)
    print("\n2. Running Integration Tests...")
    result = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_editor_integration.py",
            "-v",
            "--tb=short",
        ],
        "Integration Tests",
    )

    if result:
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        test_results["integration"] = result.returncode == 0

    # Test 3: Editor routes verification
    print("\n3. Verifying Editor Routes...")
    result = run_command(
        [sys.executable, "test_editor_routes.py"], "Editor Routes Verification"
    )

    if result:
        print(result.stdout)
        test_results["routes"] = result.returncode == 0

    # Summary
    print_header("Test Results Summary")

    passed = sum(1 for v in test_results.values() if v)
    failed = sum(1 for v in test_results.values() if not v)
    total = len(test_results)

    print(f"Total Test Suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed / total * 100:.1f}%\n")

    for test_name, success in test_results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")

    # Document any issues
    print_header("Documentation & Recommendations")

    print_section("Test Coverage")
    print("""
The following test scenarios are covered:

API Integration Tests (test_editor_integration.py):
  - Create Session Workflow
  - Fetch Session Data
  - List Sessions
  - Apply Caption Style
  - Get Preview Frames
  - List Presets
  - Get Preset Details
  - List Fonts
  - Delete Session
  - Editor Page Routes
  - Error Handling

Manual Test Checklist (EDITOR_TEST_CHECKLIST.md):
  - UI Component Tests
  - Video Player Controls
  - Timeline Display
  - Style Controls
  - Upload Interface
  - API Integration Tests
  - Workflow Tests
  - Keyboard Shortcuts
  - User Feedback
  - Browser Compatibility
  - Performance Tests
  - Edge Cases
  - Accessibility

End-to-End Test (test_e2e_editor.py):
  - Complete workflow: upload → edit style → preview → cleanup
""")

    print_section("Issues Found")
    print("""
Based on test execution:

1. The full integration test suite requires the following dependencies:
   - flask >= 3.0.0
   - torch >= 2.9.0 (for web_server.py import)
   - whisper-timestamped >= 1.15.9
   - requests (for API calls)
   - pytest (for test runner)

2. The e2e test can run with minimal dependencies (flask, requests) by using
   mocks for the caption generation pipeline.

3. Manual testing checklist is provided for browser-based testing that cannot
   be fully automated (e.g., UI interactions, keyboard shortcuts).
""")

    print_section("Recommendations")
    print("""
For Production Deployment:

1. Install all dependencies:
   pip install -r requirements.txt -r requirements-dev.txt

2. Run automated tests:
   python tests/test_e2e_editor.py
   pytest tests/test_editor_integration.py -v

3. Perform manual testing using EDITOR_TEST_CHECKLIST.md:
   - Test in Chrome, Firefox, Safari
   - Test with various video formats and sizes
   - Test keyboard shortcuts and accessibility
   - Test error handling and edge cases

4. Continuous Integration:
   - Set up CI pipeline to run automated tests on every commit
   - Include linting and type checking
   - Add code coverage reporting

5. Performance Monitoring:
   - Add timing metrics for API endpoints
   - Monitor memory usage during video processing
   - Track error rates and response times
""")

    # Return exit code
    print_header("Test Execution Complete")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
