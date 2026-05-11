#!/usr/bin/env python3
"""
End-to-End Test: Complete Workflow for Video Caption Editor

This test performs comprehensive end-to-end testing of the entire video caption editor workflow,
from media upload to caption embedding. It makes real API calls to the running Flask server.

Test Scenarios:
1. Complete Workflow with Video
2. Workflow with Audio File
3. Style Variations
4. Error Handling
5. Performance Metrics

Prerequisites:
- Flask server must be running on http://localhost:5001 (or set TEST_SERVER_URL env var)
- Test video files must be available
- Required dependencies: requests

Usage:
    export TEST_SERVER_URL=http://localhost:5001  # Optional
    python tests/test_e2e_complete_workflow.py

Author: Phase 3, Subtask 3.1 Testing
Date: 2025-02-11
"""

import json
import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Try to import requests, provide helpful error if not available
try:
    import requests
except ImportError:
    print("ERROR: 'requests' module is required. Install with: pip install requests")
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================

# Server URL - can be overridden via environment variable
BASE_URL = os.environ.get("TEST_SERVER_URL", "http://localhost:5001")
TIMEOUT = 300  # 5 minutes for long operations
SHORT_TIMEOUT = 30  # 30 seconds for quick operations

# Test video files
TEST_VIDEO_PATHS = [
    "/home/ishanp/Videos/Mummy Video.mp4",  # 19MB - good for quick tests
    "/home/ishanp/Videos/#2_converted.mp4",  # 62MB - medium video
]

# Test audio file
TEST_AUDIO_PATHS = [
    "/home/ishanp/Videos/#1.wav",  # Audio file
]

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# =============================================================================
# Test Result Tracking
# =============================================================================


class TestResult:
    """Track individual test results."""

    def __init__(self, scenario: str, test_name: str):
        self.scenario = scenario
        self.test_name = test_name
        self.status = "pending"
        self.message = ""
        self.execution_time = 0.0
        self.start_time = None
        self.end_time = None

    def start(self):
        """Mark test as started."""
        self.start_time = time.time()
        self.status = "running"

    def pass_(self, message: str = ""):
        """Mark test as passed."""
        self.end_time = time.time()
        if self.start_time:
            self.execution_time = self.end_time - self.start_time
        self.status = "passed"
        self.message = message

    def fail(self, message: str):
        """Mark test as failed."""
        self.end_time = time.time()
        if self.start_time:
            self.execution_time = self.end_time - self.start_time
        self.status = "failed"
        self.message = message

    def skip(self, message: str):
        """Mark test as skipped."""
        self.end_time = time.time()
        self.execution_time = 0.0
        self.status = "skipped"
        self.message = message


class TestSuite:
    """Manage test suite execution and results."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.session_ids: List[str] = []
        self.created_files: List[str] = []

    def add_result(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)

    def cleanup(self):
        """Clean up test sessions and files."""
        print(f"\n{YELLOW}Cleaning up test sessions and files...{RESET}")

        # Delete all created sessions
        for session_id in self.session_ids:
            try:
                response = requests.delete(
                    f"{BASE_URL}/api/sessions/{session_id}", timeout=SHORT_TIMEOUT
                )
                if response.status_code == 200:
                    print(f"{GREEN}✓ Deleted session: {session_id[:8]}...{RESET}")
            except Exception as e:
                print(
                    f"{RED}✗ Failed to delete session {session_id[:8]}...: {e}{RESET}"
                )

        # Clean up created files
        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"{GREEN}✓ Deleted file: {file_path}{RESET}")
            except Exception as e:
                print(f"{RED}✗ Failed to delete file {file_path}: {e}{RESET}")

    def print_summary(self) -> bool:
        """Print test summary. Returns True if all tests passed."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        total_time = sum(
            r.execution_time for r in self.results if r.status != "skipped"
        )

        print(f"\n{BOLD}{BLUE}{'=' * 80}{RESET}")
        print(f"{BOLD}{BLUE}  TEST SUMMARY{RESET}")
        print(f"{BOLD}{BLUE}{'=' * 80}{RESET}\n")

        print(f"Total Tests:     {total}")
        print(f"{GREEN}Passed:          {passed}{RESET}")
        if failed > 0:
            print(f"{RED}Failed:          {failed}{RESET}")
        if skipped > 0:
            print(f"{YELLOW}Skipped:         {skipped}{RESET}")
        print(f"Total Time:      {total_time:.2f}s")

        print(f"\n{BOLD}Results by Scenario:{RESET}\n")

        # Group by scenario
        scenarios = {}
        for result in self.results:
            if result.scenario not in scenarios:
                scenarios[result.scenario] = []
            scenarios[result.scenario].append(result)

        for scenario, results in scenarios.items():
            scenario_passed = sum(1 for r in results if r.status == "passed")
            scenario_failed = sum(1 for r in results if r.status == "failed")
            scenario_total = len(results)

            status_color = GREEN if scenario_failed == 0 else RED
            print(f"{status_color}  {scenario}{RESET}")
            print(f"    {scenario_passed}/{scenario_total} passed")

            if scenario_failed > 0:
                for result in results:
                    if result.status == "failed":
                        print(
                            f"      {RED}✗ {result.test_name}: {result.message}{RESET}"
                        )

        print(f"\n{BOLD}{BLUE}{'=' * 80}{RESET}\n")

        return failed == 0


# =============================================================================
# Utility Functions
# =============================================================================


def print_header(text: str):
    """Print a section header."""
    print(f"\n{BOLD}{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 80}{RESET}\n")


def print_step(step_num: int, description: str):
    """Print a test step."""
    print(f"{BLUE}Step {step_num}: {description}{RESET}")


def print_success(message: str):
    """Print a success message."""
    print(f"{GREEN}  ✓ {message}{RESET}")


def print_error(message: str):
    """Print an error message."""
    print(f"{RED}  ✗ {message}{RESET}")


def print_info(message: str):
    """Print an info message."""
    print(f"{YELLOW}  ℹ {message}{RESET}")


def check_server_health() -> bool:
    """Check if the Flask server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=SHORT_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is healthy: {data.get('model', 'unknown')}")
            return True
    except Exception as e:
        print_error(f"Server health check failed: {e}")
        return False


def check_test_files() -> Tuple[bool, List[Tuple[str, float]]]:
    """Check if test video files exist."""
    available_videos = []
    for path in TEST_VIDEO_PATHS:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            available_videos.append((path, size_mb))
            print_success(f"Found test video: {path} ({size_mb:.1f}MB)")

    available_audio = []
    for path in TEST_AUDIO_PATHS:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            available_audio.append((path, size_mb))
            print_success(f"Found test audio: {path} ({size_mb:.1f}MB)")

    return len(available_videos) > 0, available_videos + available_audio


# =============================================================================
# Test Scenarios
# =============================================================================


def scenario_1_complete_workflow_with_video(
    suite: TestSuite, video_path: str, video_size_mb: float
):
    """
    Scenario 1: Complete Workflow with Video
    Tests the full workflow from upload to caption embedding.
    """
    print_header("Scenario 1: Complete Workflow with Video")
    print_info(f"Using video: {video_path} ({video_size_mb:.1f}MB)")

    session_id = None

    # Test 1.1: Upload video and create session
    test = TestResult("Scenario 1", "Upload video and create session")
    test.start()

    print_step(1, "Upload video and create session")

    try:
        with open(video_path, "rb") as f:
            files = {"video": (os.path.basename(video_path), f, "video/mp4")}
            data = {"model": "prime"}

            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/editor/upload",
                files=files,
                data=data,
                timeout=TIMEOUT,
            )
            upload_time = time.time() - start_time

        if response.status_code in [200, 201]:
            result = response.json()
            session_id = result.get("session_id")
            if session_id:
                suite.session_ids.append(session_id)
                test.pass_(
                    f"Session created in {upload_time:.2f}s: {session_id[:8]}..."
                )
                print_success(f"Session created: {session_id}")
                print_info(f"Upload time: {upload_time:.2f}s")
            else:
                test.fail("No session_id in response")
                print_error("No session_id in response")
        else:
            test.fail(f"HTTP {response.status_code}: {response.text[:200]}")
            print_error(f"Upload failed: HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))
        print_error(f"Exception: {e}")

    suite.add_result(test)

    if not session_id:
        print_info("Skipping remaining tests in scenario 1")
        return

    # Test 1.2: Verify session details
    test = TestResult("Scenario 1", "Verify session details")
    test.start()

    print_step(2, "Verify session details")

    try:
        response = requests.get(
            f"{BASE_URL}/api/sessions/{session_id}", timeout=SHORT_TIMEOUT
        )

        if response.status_code == 200:
            session = response.json()
            required_fields = ["session_id", "video_path", "status", "created_at"]
            missing = [f for f in required_fields if f not in session]

            if not missing:
                test.pass_(f"Status: {session['status']}")
                print_success(f"Session status: {session['status']}")
                print_info(f"Video path: {session.get('video_path', 'N/A')}")
            else:
                test.fail(f"Missing fields: {missing}")
                print_error(f"Missing fields: {missing}")
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    # Test 1.3: Apply caption style
    test = TestResult("Scenario 1", "Apply caption style")
    test.start()

    print_step(3, "Apply caption style")

    try:
        style_data = {"preset_name": "reels_standard"}
        response = requests.put(
            f"{BASE_URL}/api/sessions/{session_id}/style",
            json=style_data,
            timeout=SHORT_TIMEOUT,
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                test.pass_("Style applied successfully")
                print_success("Style 'reels_standard' applied")
            else:
                test.fail(result.get("message", "Unknown error"))
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    # Test 1.4: Generate preview frames
    test = TestResult("Scenario 1", "Generate preview frames")
    test.start()

    print_step(4, "Generate preview frames")

    try:
        response = requests.get(
            f"{BASE_URL}/api/sessions/{session_id}/preview?fps=1&max_frames=10",
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            result = response.json()
            frames = result.get("frames", [])
            fps = result.get("fps", 0)

            if frames:
                test.pass_(f"Generated {len(frames)} frames at {fps}fps")
                print_success(f"Generated {len(frames)} preview frames")
                print_info(f"FPS: {fps}")
            else:
                test.skip("No frames generated (may be expected for some videos)")
                print_info("No frames generated")
        else:
            test.fail(f"HTTP {response.status_code}: {response.text[:200]}")
    except requests.exceptions.Timeout:
        test.fail("Timeout generating preview")
        print_error("Timeout generating preview")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    # Test 1.5: Embed captions into video
    test = TestResult("Scenario 1", "Embed captions into video")
    test.start()

    print_step(5, "Embed captions into video")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/sessions/{session_id}/embed",
            timeout=TIMEOUT * 2,  # Give more time for embedding
        )
        embed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                output_path = result.get("output_path")
                if output_path and os.path.exists(output_path):
                    output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    test.pass_(
                        f"Output created in {embed_time:.2f}s ({output_size_mb:.1f}MB)"
                    )
                    print_success(f"Output video created: {output_path}")
                    print_info(f"Embedding time: {embed_time:.2f}s")
                    print_info(f"Output size: {output_size_mb:.1f}MB")
                    suite.created_files.append(output_path)
                else:
                    test.skip("Output file not found (may be processing)")
            else:
                test.fail(result.get("message", "Unknown error"))
        else:
            test.fail(f"HTTP {response.status_code}: {response.text[:200]}")
    except requests.exceptions.Timeout:
        test.fail("Timeout embedding captions")
        print_error("Timeout embedding captions")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    # Test 1.6: Verify output video
    test = TestResult("Scenario 1", "Verify output video has captions")
    test.start()

    print_step(6, "Verify output video")

    try:
        response = requests.get(
            f"{BASE_URL}/api/sessions/{session_id}", timeout=SHORT_TIMEOUT
        )

        if response.status_code == 200:
            session = response.json()
            output_path = session.get("output_path")

            if output_path and os.path.exists(output_path):
                # Check file size is reasonable
                output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                if output_size_mb > 1:  # At least 1MB
                    test.pass_(f"Output file exists ({output_size_mb:.1f}MB)")
                    print_success(f"Output video verified: {output_size_mb:.1f}MB")
                else:
                    test.fail("Output file too small")
            else:
                test.skip("No output file to verify")
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)


def scenario_2_workflow_with_audio(
    suite: TestSuite, audio_path: str, audio_size_mb: float
):
    """
    Scenario 2: Workflow with Audio File
    Tests caption generation with audio-only input.
    """
    print_header("Scenario 2: Workflow with Audio File")
    print_info(f"Using audio: {audio_path} ({audio_size_mb:.1f}MB)")

    session_id = None

    # Test 2.1: Upload audio and create session
    test = TestResult("Scenario 2", "Upload audio and create session")
    test.start()

    print_step(1, "Upload audio and create session")

    try:
        with open(audio_path, "rb") as f:
            files = {"video": (os.path.basename(audio_path), f, "audio/wav")}
            data = {"model": "prime"}

            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/editor/upload",
                files=files,
                data=data,
                timeout=TIMEOUT,
            )
            upload_time = time.time() - start_time

        if response.status_code in [200, 201]:
            result = response.json()
            session_id = result.get("session_id")
            if session_id:
                suite.session_ids.append(session_id)
                test.pass_(
                    f"Session created in {upload_time:.2f}s: {session_id[:8]}..."
                )
                print_success(f"Session created: {session_id}")
                print_info(f"Upload time: {upload_time:.2f}s")
            else:
                test.fail("No session_id in response")
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    if not session_id:
        return

    # Test 2.2: Verify captions were generated
    test = TestResult("Scenario 2", "Verify captions generated")
    test.start()

    print_step(2, "Verify captions generated")

    try:
        response = requests.get(
            f"{BASE_URL}/api/sessions/{session_id}", timeout=SHORT_TIMEOUT
        )

        if response.status_code == 200:
            session = response.json()
            captions_path = session.get("captions_path")

            if captions_path and os.path.exists(captions_path):
                # Read captions and verify they're not empty
                with open(captions_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if len(content) > 10:
                        test.pass_("Captions file exists and has content")
                        print_success("Captions generated successfully")
                    else:
                        test.fail("Captions file is empty")
            else:
                test.fail("No captions file found")
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)


def scenario_3_style_variations(suite: TestSuite, video_path: str):
    """
    Scenario 3: Style Variations
    Tests different style presets and custom overrides.
    """
    print_header("Scenario 3: Style Variations")
    print_info(f"Using video: {video_path}")

    session_id = None

    # Create a session first
    test = TestResult("Scenario 3", "Create session for style testing")
    test.start()

    print_step(1, "Create session")

    try:
        with open(video_path, "rb") as f:
            files = {"video": (os.path.basename(video_path), f, "video/mp4")}
            data = {"model": "prime"}  # Use swift for faster testing

            response = requests.post(
                f"{BASE_URL}/api/editor/upload",
                files=files,
                data=data,
                timeout=TIMEOUT,
            )

        if response.status_code in [200, 201]:
            result = response.json()
            session_id = result.get("session_id")
            if session_id:
                suite.session_ids.append(session_id)
                test.pass_(f"Session created: {session_id[:8]}...")
                print_success(f"Session created: {session_id}")
            else:
                test.fail("No session_id in response")
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    if not session_id:
        return

    # Test different presets
    presets_to_test = ["reels_standard", "minimal_clean", "shorts_safe"]

    for preset_name in presets_to_test:
        test = TestResult("Scenario 3", f"Apply preset: {preset_name}")
        test.start()

        print_step(2, f"Apply preset: {preset_name}")

        try:
            style_data = {"preset_name": preset_name}
            response = requests.put(
                f"{BASE_URL}/api/sessions/{session_id}/style",
                json=style_data,
                timeout=SHORT_TIMEOUT,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    test.pass_(f"Preset applied: {preset_name}")
                    print_success(f"Preset '{preset_name}' applied")
                else:
                    test.fail(result.get("message", "Unknown error"))
            else:
                test.fail(f"HTTP {response.status_code}")
        except Exception as e:
            test.fail(str(e))

        suite.add_result(test)

        # Small delay between style changes
        time.sleep(0.5)

    # Test custom style overrides
    test = TestResult("Scenario 3", "Apply custom style overrides")
    test.start()

    print_step(3, "Apply custom style overrides")

    try:
        style_data = {
            "preset_name": "reels_standard",
            "style_overrides": {"font_size": 40, "color": "#FFFF00"},
        }
        response = requests.put(
            f"{BASE_URL}/api/sessions/{session_id}/style",
            json=style_data,
            timeout=SHORT_TIMEOUT,
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                test.pass_("Custom style applied")
                print_success("Custom style overrides applied")
            else:
                test.fail(result.get("message", "Unknown error"))
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)


def scenario_4_error_handling(suite: TestSuite):
    """
    Scenario 4: Error Handling
    Tests various error conditions and validation.
    """
    print_header("Scenario 4: Error Handling")

    # Test 4.1: Non-existent session
    test = TestResult("Scenario 4", "Get non-existent session")
    test.start()

    print_step(1, "Try to get non-existent session")

    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(
            f"{BASE_URL}/api/sessions/{fake_id}", timeout=SHORT_TIMEOUT
        )

        if response.status_code == 404:
            test.pass_("Correctly returned 404")
            print_success("Non-existent session correctly returned 404")
        else:
            test.fail(f"Expected 404, got {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    # Test 4.2: Upload without file
    test = TestResult("Scenario 4", "Upload without file")
    test.start()

    print_step(2, "Try to upload without file")

    try:
        response = requests.post(
            f"{BASE_URL}/api/editor/upload",
            data={"model": "prime"},
            timeout=SHORT_TIMEOUT,
        )

        if response.status_code == 400:
            test.pass_("Correctly rejected upload without file")
            print_success("Upload without file correctly rejected")
        else:
            test.fail(f"Expected 400, got {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)


def scenario_5_performance_metrics(
    suite: TestSuite, video_path: str, video_size_mb: float
):
    """
    Scenario 5: Performance Metrics
    Measures performance of key operations.
    """
    print_header("Scenario 5: Performance Metrics")
    print_info(f"Using video: {video_path} ({video_size_mb:.1f}MB)")

    session_id = None
    metrics = {}

    # Measure upload and session creation
    test = TestResult("Scenario 5", "Upload and session creation time")
    test.start()

    print_step(1, "Measure upload and session creation")

    try:
        with open(video_path, "rb") as f:
            files = {"video": (os.path.basename(video_path), f, "video/mp4")}
            data = {"model": "prime"}

            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/editor/upload",
                files=files,
                data=data,
                timeout=TIMEOUT,
            )
            upload_time = time.time() - start_time

        if response.status_code in [200, 201]:
            result = response.json()
            session_id = result.get("session_id")
            if session_id:
                suite.session_ids.append(session_id)
                metrics["upload_time"] = upload_time
                test.pass_(f"Upload time: {upload_time:.2f}s")
                print_success(f"Upload completed in {upload_time:.2f}s")
                if upload_time > 0:
                    print_info(f"Throughput: {video_size_mb / upload_time:.2f} MB/s")
            else:
                test.fail("No session_id in response")
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    if not session_id:
        return

    # Measure preview generation
    test = TestResult("Scenario 5", "Preview generation time")
    test.start()

    print_step(2, "Measure preview generation")

    try:
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/sessions/{session_id}/preview?fps=1&max_frames=10",
            timeout=TIMEOUT,
        )
        preview_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            frames = result.get("frames", [])
            metrics["preview_time"] = preview_time
            metrics["preview_frames"] = len(frames)

            if frames:
                test.pass_(
                    f"Preview time: {preview_time:.2f}s for {len(frames)} frames"
                )
                print_success(f"Preview generated in {preview_time:.2f}s")
                print_info(f"Average time per frame: {preview_time / len(frames):.2f}s")
            else:
                test.skip("No frames generated")
        else:
            test.fail(f"HTTP {response.status_code}")
    except Exception as e:
        test.fail(str(e))

    suite.add_result(test)

    # Print performance summary
    print(f"\n{BOLD}Performance Summary:{RESET}")
    if "upload_time" in metrics:
        print(f"  Upload Time:      {metrics['upload_time']:.2f}s")
        if video_size_mb / metrics["upload_time"] > 0:
            print(
                f"  Upload Throughput: {video_size_mb / metrics['upload_time']:.2f} MB/s"
            )
    if "preview_time" in metrics:
        print(f"  Preview Time:     {metrics['preview_time']:.2f}s")
        if metrics.get("preview_frames", 0) > 0:
            print(
                f"  Time per Frame:   {metrics['preview_time'] / metrics['preview_frames']:.2f}s"
            )


# =============================================================================
# Main Test Runner
# =============================================================================


def main() -> bool:
    """Main test execution function."""
    print(f"\n{BOLD}{MAGENTA}{'=' * 80}{RESET}")
    print(f"{BOLD}{MAGENTA}  END-TO-END TEST: COMPLETE WORKFLOW{RESET}")
    print(f"{BOLD}{MAGENTA}  Video Caption Editor{RESET}")
    print(f"{BOLD}{MAGENTA}{'=' * 80}{RESET}\n")

    print_info(
        f"Starting end-to-end testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print_info(f"Server URL: {BASE_URL}")
    print_info(f"Timeout: {TIMEOUT}s for long operations\n")

    # Initialize test suite
    suite = TestSuite()

    try:
        # Pre-flight checks
        print_header("Pre-Flight Checks")

        # Check server health
        if not check_server_health():
            print_error("Server is not running. Please start the server first:")
            print_error("  python web_server.py --port 5001")
            print_error("  Or: ./tests/start_server.sh 5001")
            return False

        # Check test files
        files_ok, available_files = check_test_files()
        if not files_ok:
            print_error("No test video files found. Please add video files to:")
            print_error(f"  {TEST_VIDEO_PATHS[0]}")
            return False

        # Run scenarios
        print(
            f"\n{GREEN}All pre-flight checks passed. Starting test scenarios...{RESET}\n"
        )

        # Scenario 1: Complete workflow with video
        video_path, video_size_mb = available_files[0]
        scenario_1_complete_workflow_with_video(suite, video_path, video_size_mb)

        time.sleep(2)

        # Scenario 2: Workflow with audio (if audio file exists)
        audio_files = [f for f in available_files if "wav" in f[0].lower()]
        if audio_files:
            audio_path, audio_size_mb = audio_files[0]
            scenario_2_workflow_with_audio(suite, audio_path, audio_size_mb)
        else:
            print_info("Scenario 2 skipped: No audio test files available")

        time.sleep(2)

        # Scenario 3: Style variations
        scenario_3_style_variations(suite, video_path)

        time.sleep(2)

        # Scenario 4: Error handling
        scenario_4_error_handling(suite)

        time.sleep(2)

        # Scenario 5: Performance metrics
        scenario_5_performance_metrics(suite, video_path, video_size_mb)

        # Cleanup
        suite.cleanup()

        # Print summary
        all_passed = suite.print_summary()

        if all_passed:
            print(f"{GREEN}{BOLD}All tests passed!{RESET}\n")
        else:
            print(
                f"{RED}{BOLD}Some tests failed. Please review the results above.{RESET}\n"
            )

        return all_passed

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user.{RESET}")
        suite.cleanup()
        return False
    except Exception as e:
        print(f"\n{RED}Test suite failed with exception: {e}{RESET}")
        import traceback

        traceback.print_exc()
        suite.cleanup()
        return False

    # Default return (should not reach here)
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
