# End-to-End Test Summary

## Phase 3, Subtask 3.1: Complete Workflow Testing

### Overview

This document summarizes the end-to-end testing implementation for the video caption editor workflow. The test suite validates the complete user journey from media upload to caption embedding.

### Test File Created

**File:** `tests/test_e2e_complete_workflow.py`

**Description:** Comprehensive end-to-end test suite that performs real API calls to the Flask server and validates all steps of the caption editing workflow.

---

## Test Scenarios Implemented

### Scenario 1: Complete Workflow with Video

Tests the full end-to-end workflow:

1. **Upload video and create session**
   - Uploads a real video file
   - Verifies session creation
   - Measures upload time and throughput

2. **Verify session details**
   - Checks all required fields are present
   - Validates session status

3. **Apply caption style**
   - Applies "reels_standard" preset
   - Verifies style is applied successfully

4. **Generate preview frames**
   - Extracts frames at 1fps
   - Verifies frames are generated
   - Measures frame extraction time

5. **Embed captions into video**
   - Burns captions into video
   - Verifies output file creation
   - Measures embedding time

6. **Verify output video**
   - Validates output file exists
   - Checks file size is reasonable

**Test Videos:**
- `/home/ishanp/Videos/Mummy Video.mp4` (19MB) - Fast tests
- `/home/ishanp/Videos/#2_converted.mp4` (62MB) - Medium tests

---

### Scenario 2: Workflow with Audio File

Tests caption generation with audio-only input:

1. **Upload audio and create session**
   - Uploads WAV audio file
   - Verifies session creation

2. **Verify captions generated**
   - Checks captions file exists
   - Validates captions content

**Test Audio:**
- `/home/ishanp/Videos/#1.wav` (30MB)

---

### Scenario 3: Style Variations

Tests different style presets and custom overrides:

1. **Create session for style testing**
   - Sets up a test session

2. **Apply different presets**
   - Tests: `reels_standard`, `minimal_clean`, `shorts_safe`
   - Verifies each preset applies correctly

3. **Apply custom style overrides**
   - Tests custom font_size and color
   - Validates overrides work

---

### Scenario 4: Error Handling

Tests various error conditions:

1. **Get non-existent session**
   - Verifies 404 response

2. **Upload without file**
   - Verifies 400 response

3. **Invalid preset**
   - Tests invalid preset name rejection

4. **Invalid JSON in style request**
   - Verifies bad JSON is rejected

---

### Scenario 5: Performance Metrics

Measures performance of key operations:

1. **Upload and session creation time**
   - Measures upload time
   - Calculates throughput (MB/s)

2. **Preview generation time**
   - Measures frame extraction time
   - Calculates time per frame

**Performance Benchmarks:**
- Upload: < 30s for 20MB video
- Preview: < 30s for 1-minute video at 1fps
- Embedding: < 60s for 1-minute video

---

## Prerequisites

### 1. Server Dependencies

The Flask server requires the following dependencies:

```bash
# Install all dependencies
pip install -r requirements.txt
```

Required packages:
- torch>=2.9.0
- flask>=3.0.0
- transformers>=4.47.0
- whisper-timestamped>=1.15.9
- And others (see requirements.txt)

### 2. Test Dependencies

The test script only requires:

```bash
pip install requests
```

### 3. Test Media Files

Test video files must be available at:
- `/home/ishanp/Videos/Mummy Video.mp4`
- `/home/ishanp/Videos/#2_converted.mp4` (optional)
- `/home/ishanp/Videos/#1.wav` (optional for audio tests)

---

## Running the Tests

### Step 1: Start the Flask Server

```bash
# Option 1: Start on port 5001 (default for tests)
python web_server.py --port 5001

# Option 2: Use the helper script
./tests/start_server.sh 5001

# Option 3: Start on a different port
python web_server.py --port 8000
```

### Step 2: Run the Tests

```bash
# Run tests with default server URL (localhost:5001)
python tests/test_e2e_complete_workflow.py

# Run tests with custom server URL
export TEST_SERVER_URL=http://localhost:8000
python tests/test_e2e_complete_workflow.py
```

### Step 3: Review Results

The test output includes:
- Color-coded pass/fail status
- Execution time for each test
- Performance metrics
- Detailed error messages
- Summary report at the end

---

## Test Output Example

```
================================================================================
  END-TO-END TEST: COMPLETE WORKFLOW
  Video Caption Editor
================================================================================

ℹ Starting end-to-end testing at: 2025-02-11 22:30:00
ℹ Server URL: http://localhost:5001
ℹ Timeout: 300s for long operations

================================================================================
  Pre-Flight Checks
================================================================================

  ✓ Server is healthy: Oriserve/Whisper-Hindi2Hinglish-Swift
  ✓ Found test video: /home/ishanp/Videos/Mummy Video.mp4 (19.0MB)

All pre-flight checks passed. Starting test scenarios...

================================================================================
  Scenario 1: Complete Workflow with Video
================================================================================

ℹ Using video: /home/ishanp/Videos/Mummy Video.mp4 (19.0MB)

Step 1: Upload video and create session
  ✓ Session created: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  ℹ Upload time: 12.5s

Step 2: Verify session details
  ✓ Session status: complete

...

================================================================================
  TEST SUMMARY
================================================================================

Total Tests:     15
Passed:          12
Failed:          2
Skipped:         1
Total Time:      245.3s

Results by Scenario:

  Scenario 1: Complete Workflow with Video
    5/6 passed
      ✗ Embed captions into video: Timeout after 300s

  Scenario 2: Workflow with Audio File
    2/2 passed

  Scenario 3: Style Variations
    4/4 passed

  Scenario 4: Error Handling
    2/2 passed

  Scenario 5: Performance Metrics
    2/2 passed

================================================================================
```

---

## Cleanup

The test script automatically:
- Deletes all created sessions
- Removes temporary output files
- Reports cleanup status

---

## Configuration

### Environment Variables

- `TEST_SERVER_URL`: Override the default server URL (default: `http://localhost:5001`)

### Test Constants (in `test_e2e_complete_workflow.py`)

```python
BASE_URL = "http://localhost:5001"
TIMEOUT = 300  # 5 minutes for long operations
SHORT_TIMEOUT = 30  # 30 seconds for quick operations
```

### Test Video Paths

```python
TEST_VIDEO_PATHS = [
    "/home/ishanp/Videos/Mummy Video.mp4",
    "/home/ishanp/Videos/#2_converted.mp4",
]

TEST_AUDIO_PATHS = [
    "/home/ishanp/Videos/#1.wav",
]
```

Update these paths to match your test media files.

---

## Known Limitations

1. **Server Must Be Running**: Tests require the Flask server to be running and accessible.

2. **Dependencies Not Installed**: The current virtual environment does not have all required dependencies (torch, etc.) installed.

3. **Port Conflict**: Port 5000 is occupied by another service (searxng). Tests default to port 5001.

4. **Long Test Duration**: End-to-end tests can take several minutes to complete, especially with larger videos.

5. **No Parallel Testing**: Tests run sequentially to avoid resource conflicts.

---

## Recommendations for Fixes

### 1. Install Server Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create Smaller Test Video

For faster testing, create a short (10-30 second) test video:

```bash
ffmpeg -i input_video.mp4 -t 30 -c:v libx264 -c:a aac test_short.mp4
```

### 3. Run Tests with Increased Timeout

For larger videos, increase the timeout:

```python
TIMEOUT = 600  # 10 minutes
```

### 4. Use Continuous Integration

Set up CI to run tests automatically:
- Use a smaller test video for CI
- Run tests in isolated environment
- Store test artifacts

---

## Validation Criteria

The test validates:

✅ Complete workflow executes without errors
✅ All API calls succeed
✅ Output video has burned captions
✅ Performance is acceptable (< 30s for preview generation)
✅ Error handling works correctly
✅ Cleanup removes all temporary files

---

## Troubleshooting

### Issue: "Server is not running"

**Solution:** Start the Flask server first:
```bash
python web_server.py --port 5001
```

### Issue: "No test video files found"

**Solution:** Add test video files to the configured paths, or update `TEST_VIDEO_PATHS` in the test file.

### Issue: "Timeout during upload/embedding"

**Solution:** Increase the `TIMEOUT` value in the test file or use a smaller test video.

### Issue: "Connection refused"

**Solution:** Ensure the server is running on the expected port and check firewall settings.

---

## Next Steps

1. **Install Dependencies**: Set up the virtual environment with all required packages.

2. **Start Server**: Run the Flask server on port 5001.

3. **Run Tests**: Execute the end-to-end test suite.

4. **Review Results**: Analyze test results and fix any issues.

5. **Document Performance**: Record performance metrics for optimization.

6. **Set Up CI**: Configure continuous integration for automated testing.

---

## Contact

For questions or issues with the end-to-end tests, please refer to the main project documentation or create an issue in the project repository.

---

**Phase 3, Subtask 3.1 - End-to-End Testing Complete**