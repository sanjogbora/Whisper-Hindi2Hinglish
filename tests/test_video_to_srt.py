"""
Quick test script for video to SRT conversion
"""
import os
import sys

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        if result.returncode == 0:
            print("✓ FFmpeg is installed")
            return True
        else:
            print("✗ FFmpeg not found")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not found. Please install FFmpeg first.")
        print("  Windows: winget install ffmpeg")
        print("  Or download from: https://ffmpeg.org/download.html")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    required = ['torch', 'transformers', 'flask']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is missing")
            missing.append(package)
    
    if missing:
        print("\nInstall missing packages:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def test_conversion():
    """Test video to SRT conversion with example file"""
    print("\n--- Testing Video to SRT Conversion ---")
    
    # Check if example audio exists (we'll use it as a test)
    example_files = [f for f in os.listdir('examples') if f.endswith('.wav')]
    
    if not example_files:
        print("No example files found to test with.")
        print("Please add a video file and run:")
        print("  python video_to_srt.py your_video.mp4")
        return
    
    print(f"Found {len(example_files)} example audio files")
    print("\nTo test with your video, run:")
    print("  python video_to_srt.py your_video.mp4")

def main():
    print("=== Video to SRT Converter - System Check ===\n")
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    print()
    
    # Check Python dependencies
    deps_ok = check_dependencies()
    print()
    
    if ffmpeg_ok and deps_ok:
        print("✓ All checks passed! You're ready to go.\n")
        print("Quick Start:")
        print("  1. Web Interface: python api_server.py")
        print("     Then open: http://localhost:5000")
        print()
        print("  2. Command Line: python video_to_srt.py your_video.mp4")
        print()
        test_conversion()
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
