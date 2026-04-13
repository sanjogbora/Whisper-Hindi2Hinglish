#!/usr/bin/env python3
"""
Custom SRT generator with 3 words max and optimal character count
"""

import sys
import whisper_timestamped as whisper
from caption_generator import format_timestamp
from media_handler import get_media_duration


def generate_compact_srt(audio_path, output_path):
    """Generate SRT with max 3 words per subtitle"""

    print(f"Loading audio from {audio_path}...")
    device = "cpu"
    model = whisper.load_model("Oriserve/Whisper-Hindi2Hinglish-Prime", device=device)
    audio = whisper.load_audio(audio_path)

    print("Transcribing...")
    result = whisper.transcribe(
        model,
        audio,
        language="hi",
        vad=False,
        condition_on_previous_text=False,
        remove_empty_words=True,
    )

    segments = result.get("segments", [])
    all_words = []

    for seg in segments:
        if "words" in seg and seg["words"]:
            all_words.extend(seg["words"])

    print(f"Total words: {len(all_words)}")

    # Group into subtitles (max 3 words)
    subtitles = []
    i = 0

    while i < len(all_words):
        # Get up to 3 words
        words_chunk = []
        total_chars = 0
        j = i

        while j < len(all_words) and len(words_chunk) < 3:
            word = all_words[j]
            word_text = word.get("text", "").strip()

            # Check character limit (including spaces)
            if words_chunk:
                new_total = total_chars + 1 + len(word_text)
            else:
                new_total = total_chars + len(word_text)

            if new_total > 30 and len(words_chunk) > 0:
                break  # Exceeded character limit

            words_chunk.append(word)
            total_chars = new_total
            j += 1

        if words_chunk:
            start_time = words_chunk[0].get("start", 0)
            end_time = words_chunk[-1].get("end", start_time + 1)
            text = " ".join([w.get("text", "") for w in words_chunk])
            subtitles.append((text, start_time, end_time))

        i = j

    # Write SRT file
    print(f"Writing {len(subtitles)} subtitles to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        for i, (text, start, end) in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")

    print(f"✓ Generated {len(subtitles)} subtitles")

    # Show statistics
    word_counts = [len(s[0].split()) for s in subtitles]
    char_counts = [len(s[0]) for s in subtitles]

    print(f"\nStatistics:")
    print(f"  Total subtitles: {len(subtitles)}")
    print(f"  Avg words: {sum(word_counts) / len(word_counts):.1f}")
    print(f"  Max words: {max(word_counts)}")
    print(f"  Avg chars: {sum(char_counts) / len(char_counts):.1f}")
    print(f"  Max chars: {max(char_counts)}")


if __name__ == "__main__":
    audio_path = "/home/ishanp/Videos/#8.wav"
    output_path = "/home/ishanp/Videos/#8.srt"

    generate_compact_srt(audio_path, output_path)
