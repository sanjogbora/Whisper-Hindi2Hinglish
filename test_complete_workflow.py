#!/usr/bin/env python3
"""
End-to-End Test: Complete Workflow for Video Caption Editor
Tests using the correct API endpoints with proper model mapping
"""

import json
import os
import sys
import time
import requests
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5001"
TIMEOUT = 600  # 10 minutes for long operations
SHORT_TIMEOUT = 30

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Test video file
TEST_VIDEO = "/home/ishanp/Videos/#2_converted.mp4"


def print_header(text):
    print(f"\n{BOLD}{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 80}{RESET}\n")


def print_step(step_num, description):
    print(f"{BLUE}Step {step_num}: {description}{RESET}")


def print_success(message):
    print(f"{GREEN}  ✓ {message}{RESET}")


def print_error(message):
    print(f"{RED}  ✗ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}  ℹ {message}{RESET}")


def main():
    print_header("E2E TEST: Video Caption Editor Complete Workflow")
    print_info(f"Test video: {TEST_VIDEO}")
    print_info(f"Server URL: {BASE_URL}")
    print_info(f"Starting at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Verify video file exists
    if not os.path.exists(TEST_VIDEO):
        print_error(f"Video file not found: {TEST_VIDEO}")
        return False

    video_size_mb = os.path.getsize(TEST_VIDEO) / (1024 * 1024)
    print_info(f"Video size: {video_size_mb:.1f}MB\n")

    # Check server health
    print_step(0, "Check server health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=SHORT_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server healthy: {data.get('model', 'unknown')}")
        else:
            print_error(f"Server unhealthy: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect to server: {e}")
        return False

    session_id = None
    test_results = []

    # ========================================
    # Step 1: Upload video and create session
    # ========================================
    print_step(1, "Upload video and create session")
    test_results.append(("Upload video", False, ""))

    try:
        with open(TEST_VIDEO, "rb") as f:
            files = {"video": (os.path.basename(TEST_VIDEO), f, "video/mp4")}
            data = {"model": "prime"}  # Use the correct model name

            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/video/upload", files=files, data=data, timeout=TIMEOUT
            )
            upload_time = time.time() - start_time

        if response.status_code in [200, 201]:
            result = response.json()
            session_id = result.get("session_id")
            if session_id:
                test_results[-1] = (
                    "Upload video",
                    True,
                    f"Session: {session_id[:8]}... in {upload_time:.1f}s",
                )
                print_success(f"Session created: {session_id}")
                print_info(f"Upload time: {upload_time:.1f}s")
                print_info(f"Status: {result.get('status', 'unknown')}")
            else:
                test_results[-1] = ("Upload video", False, "No session_id in response")
                print_error("No session_id in response")
        else:
            error_msg = (
                response.text[:200] if response.text else f"HTTP {response.status_code}"
            )
            test_results[-1] = ("Upload video", False, error_msg)
            print_error(f"Upload failed: {error_msg}")
            print_error(f"Full response: {response.text[:500]}")
            return False
    except Exception as e:
        test_results[-1] = ("Upload video", False, str(e))
        print_error(f"Exception: {e}")
        return False

    if not session_id:
        print_error("No session ID, stopping test")
        return False

    time.sleep(2)

    # ========================================
    # Step 2: Get session info
    # ========================================
    print_step(2, "Get session info")
    test_results.append(("Get session info", False, ""))

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/{session_id}", timeout=SHORT_TIMEOUT
        )

        if response.status_code == 200:
            session = response.json()
            test_results[-1] = (
                "Get session info",
                True,
                f"Status: {session.get('status')}",
            )
            print_success(f"Session retrieved successfully")
            print_info(f"Status: {session.get('status')}")
            print_info(f"Video path: {session.get('video_path', 'N/A')}")
            print_info(f"Captions path: {session.get('captions_path', 'N/A')}")
        else:
            error_msg = response.text[:200]
            test_results[-1] = ("Get session info", False, error_msg)
            print_error(f"Failed: {error_msg}")
    except Exception as e:
        test_results[-1] = ("Get session info", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Step 3: Wait for caption generation
    # ========================================
    print_step(3, "Wait for caption generation (may take 1-2 minutes)")
    test_results.append(("Caption generation", False, ""))

    max_wait = 180  # 3 minutes
    check_interval = 10
    elapsed = 0

    while elapsed < max_wait:
        try:
            response = requests.get(
                f"{BASE_URL}/api/video/{session_id}", timeout=SHORT_TIMEOUT
            )

            if response.status_code == 200:
                session = response.json()
                status = session.get("status")
                captions_path = session.get("captions_path")

                print_info(f"Status: {status} (elapsed: {elapsed}s)")

                if status == "transcribed" and captions_path:
                    # Verify captions file exists
                    if os.path.exists(captions_path):
                        with open(captions_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            caption_count = content.strip().count("\n\n") + 1
                        test_results[-1] = (
                            "Caption generation",
                            True,
                            f"{caption_count} captions",
                        )
                        print_success(f"Captions generated: {caption_count} captions")
                        break
                    else:
                        print_error(f"Captions file not found: {captions_path}")
                        break
                elif status == "error":
                    error_msg = session.get("error", "Unknown error")
                    test_results[-1] = ("Caption generation", False, error_msg)
                    print_error(f"Caption generation failed: {error_msg}")
                    break
                elif status in ["processing", "transcribing"]:
                    # Still processing, wait and check again
                    time.sleep(check_interval)
                    elapsed += check_interval
                else:
                    print_info(f"Unexpected status: {status}")
                    time.sleep(check_interval)
                    elapsed += check_interval
            else:
                test_results[-1] = (
                    "Caption generation",
                    False,
                    f"HTTP {response.status_code}",
                )
                print_error(f"Failed to check status: HTTP {response.status_code}")
                break
        except Exception as e:
            test_results[-1] = ("Caption generation", False, str(e))
            print_error(f"Exception: {e}")
            break

    if elapsed >= max_wait:
        test_results[-1] = ("Caption generation", False, "Timeout after 3 minutes")
        print_error("Caption generation timeout")

    # ========================================
    # Step 4: List style presets
    # ========================================
    print_step(4, "List style presets")
    test_results.append(("List styles", False, ""))

    try:
        response = requests.get(f"{BASE_URL}/api/presets", timeout=SHORT_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            presets = data.get("presets", [])
            preset_names = [p.get("id") for p in presets]
            test_results[-1] = ("List styles", True, f"{len(presets)} presets")
            print_success(f"Found {len(presets)} presets")
            print_info(f"Presets: {', '.join(preset_names)}")
        else:
            test_results[-1] = ("List styles", False, f"HTTP {response.status_code}")
            print_error(f"Failed: HTTP {response.status_code}")
    except Exception as e:
        test_results[-1] = ("List styles", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Step 5: Apply a style
    # ========================================
    print_step(5, "Apply style preset")
    test_results.append(("Apply style", False, ""))

    try:
        style_data = {"preset_name": "modern"}
        response = requests.put(
            f"{BASE_URL}/api/video/{session_id}/style",
            json=style_data,
            timeout=SHORT_TIMEOUT,
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                test_results[-1] = ("Apply style", True, "Style applied")
                print_success(f"Style 'modern' applied successfully")
            else:
                test_results[-1] = (
                    "Apply style",
                    False,
                    result.get("message", "Unknown error"),
                )
                print_error(f"Failed: {result.get('message', 'Unknown error')}")
        else:
            test_results[-1] = ("Apply style", False, f"HTTP {response.status_code}")
            print_error(f"Failed: HTTP {response.status_code}")
    except Exception as e:
        test_results[-1] = ("Apply style", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Step 6: Get preview frames
    # ========================================
    print_step(6, "Get preview frames")
    test_results.append(("Get frames", False, ""))

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/{session_id}/preview?fps=1&max_frames=10",
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            frames = data.get("frames", [])
            test_results[-1] = ("Get frames", True, f"{len(frames)} frames")
            print_success(f"Generated {len(frames)} preview frames")
            if frames:
                print_info(f"First frame at: {frames[0].get('timestamp', 0)}s")
        else:
            error_msg = response.text[:200]
            test_results[-1] = ("Get frames", False, error_msg)
            print_error(f"Failed: {error_msg}")
    except Exception as e:
        test_results[-1] = ("Get frames", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Step 7: Generate preview frame
    # ========================================
    print_step(7, "Generate captioned preview frame at timestamp 5.0s")
    test_results.append(("Preview frame", False, ""))

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/{session_id}/preview/frame?t=5.0",
            timeout=SHORT_TIMEOUT,
        )

        if response.status_code == 200:
            # Check if we got an image back
            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                test_results[-1] = (
                    "Preview frame",
                    True,
                    f"{len(response.content)} bytes",
                )
                print_success(
                    f"Preview frame generated ({len(response.content)} bytes)"
                )
            else:
                test_results[-1] = (
                    "Preview frame",
                    False,
                    f"Not an image: {content_type}",
                )
                print_error(f"Response not an image: {content_type}")
        else:
            error_msg = response.text[:200]
            test_results[-1] = ("Preview frame", False, error_msg)
            print_error(f"Failed: {error_msg}")
    except Exception as e:
        test_results[-1] = ("Preview frame", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Step 8: Render video with captions
    # ========================================
    print_step(8, "Render video with captions")
    test_results.append(("Render video", False, ""))

    try:
        response = requests.post(
            f"{BASE_URL}/api/video/{session_id}/render",
            json={"quality": "high"},
            timeout=TIMEOUT * 2,
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                render_id = result.get("render_id")
                estimated_time = result.get("estimated_time", 0)
                test_results[-1] = (
                    "Render video",
                    True,
                    f"Render ID: {render_id[:8]}...",
                )
                print_success(f"Rendering started (ID: {render_id})")
                print_info(f"Estimated time: {estimated_time}s")
            else:
                test_results[-1] = (
                    "Render video",
                    False,
                    result.get("message", "Unknown error"),
                )
                print_error(f"Failed: {result.get('message', 'Unknown error')}")
        else:
            error_msg = response.text[:200]
            test_results[-1] = ("Render video", False, error_msg)
            print_error(f"Failed: {error_msg}")
    except Exception as e:
        test_results[-1] = ("Render video", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Step 9: Monitor rendering progress
    # ========================================
    print_step(9, "Monitor rendering progress (may take 3-5 minutes)")
    test_results.append(("Rendering progress", False, ""))

    max_wait = 360  # 6 minutes
    check_interval = 15
    elapsed = 0

    while elapsed < max_wait:
        try:
            response = requests.get(
                f"{BASE_URL}/api/video/{session_id}/render/progress",
                timeout=SHORT_TIMEOUT,
            )

            if response.status_code == 200:
                progress = response.json()
                status = progress.get("status")
                percent = progress.get("percent", 0)

                print_info(f"Rendering: {status} ({percent}%) - elapsed: {elapsed}s")

                if status == "complete":
                    test_results[-1] = (
                        "Rendering progress",
                        True,
                        f"Completed in {elapsed}s",
                    )
                    print_success(f"Rendering completed in {elapsed}s")
                    break
                elif status == "error":
                    test_results[-1] = ("Rendering progress", False, "Rendering failed")
                    print_error("Rendering failed")
                    break
                elif status in ["queued", "rendering"]:
                    time.sleep(check_interval)
                    elapsed += check_interval
                else:
                    print_info(f"Unexpected status: {status}")
                    time.sleep(check_interval)
                    elapsed += check_interval
            else:
                test_results[-1] = (
                    "Rendering progress",
                    False,
                    f"HTTP {response.status_code}",
                )
                print_error(f"Failed to check progress: HTTP {response.status_code}")
                break
        except Exception as e:
            test_results[-1] = ("Rendering progress", False, str(e))
            print_error(f"Exception: {e}")
            break

    if elapsed >= max_wait:
        test_results[-1] = ("Rendering progress", False, "Timeout after 6 minutes")
        print_error("Rendering timeout")

    # ========================================
    # Step 10: Download captioned video
    # ========================================
    print_step(10, "Download captioned video")
    test_results.append(("Download video", False, ""))

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/{session_id}/download", timeout=SHORT_TIMEOUT
        )

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "video" in content_type:
                video_size = len(response.content)
                test_results[-1] = (
                    "Download video",
                    True,
                    f"{video_size / (1024 * 1024):.1f}MB",
                )
                print_success(f"Video downloaded: {video_size / (1024 * 1024):.1f}MB")
            else:
                test_results[-1] = (
                    "Download video",
                    False,
                    f"Not video: {content_type}",
                )
                print_error(f"Response not video: {content_type}")
        else:
            error_msg = response.text[:200]
            test_results[-1] = ("Download video", False, error_msg)
            print_error(f"Failed: {error_msg}")
    except Exception as e:
        test_results[-1] = ("Download video", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Step 11: Verify final output
    # ========================================
    print_step(11, "Verify final output file")
    test_results.append(("Verify output", False, ""))

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/{session_id}", timeout=SHORT_TIMEOUT
        )

        if response.status_code == 200:
            session = response.json()
            output_path = session.get("metadata", {}).get("output_path")

            if output_path and os.path.exists(output_path):
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                test_results[-1] = ("Verify output", True, f"{file_size_mb:.1f}MB")
                print_success(f"Output file verified: {file_size_mb:.1f}MB")
                print_info(f"Output path: {output_path}")
            else:
                test_results[-1] = ("Verify output", False, "Output file not found")
                print_error("Output file not found")
        else:
            test_results[-1] = ("Verify output", False, f"HTTP {response.status_code}")
            print_error(f"Failed: HTTP {response.status_code}")
    except Exception as e:
        test_results[-1] = ("Verify output", False, str(e))
        print_error(f"Exception: {e}")

    # ========================================
    # Print summary
    # ========================================
    print_header("TEST SUMMARY")

    passed = sum(1 for _, success, _ in test_results if success)
    failed = sum(1 for _, success, _ in test_results if not success)
    total = len(test_results)

    print(f"Total Tests:     {total}")
    print(f"{GREEN}Passed:          {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed:          {failed}{RESET}")

    print(f"\nDetailed Results:")
    for i, (test_name, success, details) in enumerate(test_results, 1):
        status_color = GREEN if success else RED
        status_icon = "✓" if success else "✗"
        print(f"{status_color}  {i}. {test_name}: {status_icon}{RESET}")
        if details:
            print(f"     {details}")

    print(f"\n{BOLD}Session ID: {session_id}{RESET}")

    all_passed = failed == 0

    if all_passed:
        print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}\n")
    else:
        print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED{RESET}\n")

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
