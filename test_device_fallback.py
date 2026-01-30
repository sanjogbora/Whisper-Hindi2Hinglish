"""
Test script to verify automatic device detection and CPU fallback
"""
import torch
from utils import get_device
from logger import logger

def test_device_detection():
    """Test automatic device detection"""
    print("\n" + "="*60)
    print("Testing Device Detection")
    print("="*60)

    # Check if CUDA is available
    cuda_available = torch.cuda.is_available()
    print(f"\nCUDA available: {cuda_available}")

    if cuda_available:
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Test with preferred device = cuda
    print("\n--- Test 1: Requesting CUDA ---")
    device = get_device("cuda")
    print(f"Returned device: {device}")

    # Test with preferred device = cpu
    print("\n--- Test 2: Requesting CPU ---")
    device = get_device("cpu")
    print(f"Returned device: {device}")

    print("\n" + "="*60)
    print("✓ Device detection test complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_device_detection()
