"""
Example: How to use the Video to SRT API programmatically
"""
import requests
import os

# Configuration
API_URL = "http://localhost:5000"
VIDEO_FILE = "your_video.mp4"  # Change this to your video file
OUTPUT_SRT = "output.srt"
MODEL = "swift"  # or "prime" for better quality

def convert_video_to_srt(video_path, output_path, model="swift"):
    """
    Convert video to SRT using the API
    
    Args:
        video_path: Path to input video file
        output_path: Path to save SRT file
        model: "swift" (faster) or "prime" (better quality)
    """
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    print(f"Converting {video_path} to SRT...")
    print(f"Using model: {model}")
    
    # Prepare the request
    with open(video_path, 'rb') as video_file:
        files = {'video': video_file}
        data = {'model': model}
        
        # Send request
        try:
            response = requests.post(
                f"{API_URL}/upload",
                files=files,
                data=data,
                timeout=600  # 10 minutes timeout
            )
            
            # Check response
            if response.status_code == 200:
                # Save SRT file
                with open(output_path, 'wb') as srt_file:
                    srt_file.write(response.content)
                
                print(f"✓ Success! SRT file saved to: {output_path}")
                return True
            else:
                error = response.json().get('error', 'Unknown error')
                print(f"✗ Error: {error}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("✗ Error: Cannot connect to server.")
            print("  Make sure the server is running: python api_server.py")
            return False
        except requests.exceptions.Timeout:
            print("✗ Error: Request timed out. Video might be too long.")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

def check_server_health():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is running")
            print(f"  Model: {data.get('model', 'Unknown')}")
            return True
        else:
            print("✗ Server is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running")
        print("  Start it with: python api_server.py")
        return False
    except Exception as e:
        print(f"✗ Error checking server: {e}")
        return False

def batch_convert(video_files, output_dir="srt_output", model="swift"):
    """
    Convert multiple videos to SRT files
    
    Args:
        video_files: List of video file paths
        output_dir: Directory to save SRT files
        model: "swift" or "prime"
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Batch converting {len(video_files)} videos...")
    
    results = []
    for i, video_path in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing: {video_path}")
        
        # Generate output path
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(output_dir, f"{video_name}.srt")
        
        # Convert
        success = convert_video_to_srt(video_path, output_path, model)
        results.append({
            'video': video_path,
            'srt': output_path,
            'success': success
        })
    
    # Summary
    print("\n" + "="*50)
    print("BATCH CONVERSION SUMMARY")
    print("="*50)
    successful = sum(1 for r in results if r['success'])
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    return results

# Example usage
if __name__ == "__main__":
    print("=== Video to SRT API Example ===\n")
    
    # Check if server is running
    if not check_server_health():
        print("\nPlease start the server first:")
        print("  python api_server.py")
        exit(1)
    
    print()
    
    # Example 1: Single video conversion
    print("Example 1: Single Video Conversion")
    print("-" * 40)
    
    if os.path.exists(VIDEO_FILE):
        convert_video_to_srt(VIDEO_FILE, OUTPUT_SRT, MODEL)
    else:
        print(f"Video file not found: {VIDEO_FILE}")
        print("Please update VIDEO_FILE variable with your video path")
    
    print()
    
    # Example 2: Batch conversion
    print("Example 2: Batch Conversion")
    print("-" * 40)
    
    # List of videos to convert
    video_list = [
        "video1.mp4",
        "video2.mp4",
        "video3.mp4"
    ]
    
    # Filter to only existing files
    existing_videos = [v for v in video_list if os.path.exists(v)]
    
    if existing_videos:
        batch_convert(existing_videos, output_dir="srt_output", model="swift")
    else:
        print("No video files found for batch conversion")
        print("Add your video files and update the video_list")
    
    print("\n" + "="*50)
    print("Examples complete!")
    print("="*50)
