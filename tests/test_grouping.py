"""
Unit test for the group_word_chunks function
"""
import sys
sys.path.insert(0, r'C:\Users\sanjo\Documents\Whisper-Hindi2Hinglish')

from video_to_srt import group_word_chunks

def test_group_word_chunks():
    """Test the group_word_chunks function with sample data"""

    # Test case: Simulating Whisper's word-level chunks
    # with varying gaps to test pause detection
    test_chunks = [
        {'text': 'Hello', 'timestamp': (0.0, 0.3)},      # Word 1
        {'text': ' world', 'timestamp': (0.35, 0.8)},    # Word 2 - small gap (0.05s)
        {'text': ' how', 'timestamp': (0.85, 1.2)},      # Word 3 - small gap (0.05s)
        {'text': ' are', 'timestamp': (1.25, 1.5)},      # Word 4 - small gap (0.05s)
        # Large pause here (0.9s > 0.8s threshold)
        {'text': ' you', 'timestamp': (2.4, 2.7)},       # Word 5 - new group
        {'text': ' doing', 'timestamp': (2.75, 3.2)},    # Word 6 - small gap
        {'text': ' today', 'timestamp': (3.25, 3.8)},    # Word 7 - small gap
    ]

    print("Testing group_word_chunks function...")
    print(f"\nInput: {len(test_chunks)} word-level chunks")
    for i, chunk in enumerate(test_chunks, 1):
        print(f"  {i}. '{chunk['text'].strip()}' @ {chunk['timestamp']}")

    # Run the function
    result = group_word_chunks(test_chunks, min_words=2, max_words=4, max_pause_gap=0.8)

    print(f"\nOutput: {len(result)} grouped subtitles")
    for i, (text, start, end) in enumerate(result, 1):
        duration = end - start
        word_count = len(text.split())
        print(f"  {i}. '{text}' @ {start:.2f}-{end:.2f}s ({duration:.2f}s, {word_count} words)")

    # Verify expectations
    print("\nVerification:")

    # Should have 2 groups (due to the large pause)
    expected_groups = 2
    if len(result) == expected_groups:
        print(f"[PASS] Correct number of groups: {len(result)} (expected {expected_groups})")
    else:
        print(f"[FAIL] Wrong number of groups: {len(result)} (expected {expected_groups})")

    # First group should have words 1-4 (4 words max)
    first_group_text, first_start, first_end = result[0]
    if 'Hello' in first_group_text and 'are' in first_group_text:
        print(f"[PASS] First group contains expected words")
    else:
        print(f"[FAIL] First group missing expected words")

    # Second group should have words 5-7
    second_group_text, second_start, second_end = result[1]
    if 'you' in second_group_text and 'today' in second_group_text:
        print(f"[PASS] Second group contains expected words")
    else:
        print(f"[FAIL] Second group missing expected words")

    # Verify timing preservation
    if abs(first_start - 0.0) < 0.01:  # Should start at 0.0
        print(f"[PASS] First group starts at correct time: {first_start:.2f}s")
    else:
        print(f"[FAIL] First group wrong start time: {first_start:.2f}s (expected 0.0)")

    if abs(first_end - 1.5) < 0.01:  # Should end at 1.5 (last word of group)
        print(f"[PASS] First group ends at correct time: {first_end:.2f}s")
    else:
        print(f"[FAIL] First group wrong end time: {first_end:.2f}s (expected 1.5)")

    if abs(second_start - 2.4) < 0.01:  # Should start at 2.4 (after pause)
        print(f"[PASS] Second group starts at correct time: {second_start:.2f}s")
    else:
        print(f"[FAIL] Second group wrong start time: {second_start:.2f}s (expected 2.4)")

    print("\n[SUCCESS] Test completed successfully!")
    return True

if __name__ == "__main__":
    test_group_word_chunks()
