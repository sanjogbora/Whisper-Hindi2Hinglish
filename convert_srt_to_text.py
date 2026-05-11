#!/usr/bin/env python3
"""
Convert SRT files to readable text transcripts
"""

from pathlib import Path

SRT_DIR = Path("/home/ishanp/Videos/Content-Research")
OUTPUT_DIR = Path("/home/ishanp/Videos/Content-Research/transcripts")


def parse_srt(srt_path):
    """Parse SRT file and extract text"""
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    words = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Skip empty lines
        if not line:
            i += 1
            continue
        # Skip sequence numbers (just digits)
        if line.isdigit():
            i += 1
            continue
        # Skip timestamp lines
        if "-->" in line:
            i += 1
            continue
        # This is a word/text line
        if line:
            words.append(line)
        i += 1

    return " ".join(words)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    srt_files = sorted(SRT_DIR.glob("*.srt"))
    print(f"Found {len(srt_files)} SRT files")

    for srt_file in srt_files:
        text = parse_srt(srt_file)

        # Output filename: same name but .txt
        output_file = OUTPUT_DIR / srt_file.name.replace(".srt", ".txt")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✓ {output_file.name}")

    print(f"\nDone! Created {len(srt_files)} transcript files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
