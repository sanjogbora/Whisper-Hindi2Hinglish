#!/bin/bash
# Test script for Phase 1 API endpoints
# This script tests all 10 new API endpoints

BASE_URL="http://localhost:5000"
SESSION_ID=""

echo "=========================================="
echo "Phase 1 API Endpoints Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
    fi
}

# 1. Test Health Check
echo "1. Testing Health Check..."
curl -s -X GET "$BASE_URL/health" > /dev/null
print_result $? "Health check endpoint"
echo ""

# 2. Test API Info
echo "2. Testing API Info..."
curl -s -X GET "$BASE_URL/api" | grep -q "sessions"
print_result $? "API info endpoint shows new endpoints"
echo ""

# 3. Test List Sessions (should be empty initially)
echo "3. Testing List Sessions..."
curl -s -X GET "$BASE_URL/api/sessions" | grep -q '"sessions"'
print_result $? "List sessions endpoint"
echo ""

# 4. Test List Presets
echo "4. Testing List Presets..."
curl -s -X GET "$BASE_URL/api/presets" | grep -q '"presets"'
print_result $? "List presets endpoint"
echo ""

# 5. Test Get Specific Preset
echo "5. Testing Get Preset (reels_standard)..."
curl -s -X GET "$BASE_URL/api/presets/reels_standard" | grep -q '"name"'
print_result $? "Get preset details endpoint"
echo ""

# 6. Test List Fonts
echo "6. Testing List Fonts..."
curl -s -X GET "$BASE_URL/api/fonts" | grep -q '"fonts"'
print_result $? "List fonts endpoint"
echo ""

# Note: The following tests require a video file
# Uncomment and provide a valid video path to test

# 7. Test Create Session
# echo "7. Testing Create Session..."
# SESSION_ID=$(curl -s -X POST "$BASE_URL/api/sessions" \
#   -H "Content-Type: application/json" \
#   -d "{\"media_path\": \"/path/to/video.mp4\", \"model_name\": \"prime\"}" | jq -r '.session_id')
#
# if [ "$SESSION_ID" != "null" ] && [ -n "$SESSION_ID" ]; then
#     print_result 0 "Create session endpoint (Session ID: $SESSION_ID)"
# else
#     print_result 1 "Create session endpoint"
# fi
# echo ""

# 8. Test Get Session Details
# if [ -n "$SESSION_ID" ]; then
#     echo "8. Testing Get Session Details..."
#     curl -s -X GET "$BASE_URL/api/sessions/$SESSION_ID" | grep -q '"session_id"'
#     print_result $? "Get session details endpoint"
#     echo ""
# fi

# 9. Test Apply Style
# if [ -n "$SESSION_ID" ]; then
#     echo "9. Testing Apply Style..."
#     curl -s -X PUT "$BASE_URL/api/sessions/$SESSION_ID/style" \
#       -H "Content-Type: application/json" \
#       -d '{"preset_name": "reels_standard"}' | grep -q '"success"'
#     print_result $? "Apply style endpoint"
#     echo ""
# fi

# 10. Test Get Preview Frames
# if [ -n "$SESSION_ID" ]; then
#     echo "10. Testing Get Preview Frames..."
#     curl -s -X GET "$BASE_URL/api/sessions/$SESSION_ID/preview" | grep -q '"frames"'
#     print_result $? "Get preview frames endpoint"
#     echo ""
# fi

# 11. Test Embed Captions
# if [ -n "$SESSION_ID" ]; then
#     echo "11. Testing Embed Captions..."
#     curl -s -X POST "$BASE_URL/api/sessions/$SESSION_ID/embed" \
#       -H "Content-Type: application/json" \
#       -d '{"burn": true}' | grep -q '"output_path"'
#     print_result $? "Embed captions endpoint"
#     echo ""
# fi

# 12. Test Delete Session
# if [ -n "$SESSION_ID" ]; then
#     echo "12. Testing Delete Session..."
#     curl -s -X DELETE "$BASE_URL/api/sessions/$SESSION_ID" | grep -q '"success"'
#     print_result $? "Delete session endpoint"
#     echo ""
# fi

echo "=========================================="
echo "Basic endpoint tests completed!"
echo "=========================================="
echo ""
echo "Note: Tests 7-12 require a valid video file."
echo "Uncomment and modify the script to test those endpoints."
echo ""
echo "Example curl commands:"
echo ""
echo "# Create a session:"
echo 'curl -X POST http://localhost:5000/api/sessions \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{"media_path": "/path/to/video.mp4", "model_name": "prime"}'\'
echo ""
echo "# Get session details:"
echo 'curl http://localhost:5000/api/sessions/{session_id}'
echo ""
echo "# Apply style:"
echo 'curl -X PUT http://localhost:5000/api/sessions/{session_id}/style \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{"preset_name": "reels_standard"}'\'
echo ""
echo "# Get preview frames:"
echo 'curl "http://localhost:5000/api/sessions/{session_id}/preview?fps=1&max_frames=60"'
echo ""
echo "# Embed captions:"
echo 'curl -X POST http://localhost:5000/api/sessions/{session_id}/embed \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{"output_path": "/path/to/output.mp4", "burn": true}'\'
echo ""
echo "# Delete session:"
echo 'curl -X DELETE http://localhost:5000/api/sessions/{session_id}'