#!/usr/bin/env python3
"""
Integration test for FAL service
Tests the image editing functionality without needing the Flask server
"""

import sys
import base64
from dotenv import load_dotenv
from fal_service import get_fal_service

# Load environment variables
load_dotenv()

def test_fal_integration(image_path, prompt="add a sunset background"):
    """Test the FAL service integration"""

    print("="*60)
    print("FAL.AI Integration Test")
    print("="*60)

    # Read and encode the image
    print(f"\n1. Reading image: {image_path}")
    with open(image_path, 'rb') as f:
        image_data = f.read()
    print(f"   Image size: {len(image_data)} bytes")

    # Get FAL service
    print(f"\n2. Initializing FAL service...")
    try:
        fal_service = get_fal_service()
        print("   ✓ FAL service initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize FAL service: {e}")
        return False

    # Edit the image
    print(f"\n3. Editing image with prompt: '{prompt}'")
    try:
        result = fal_service.edit_image(
            prompt=prompt,
            image_data=image_data,
            filename=image_path.split('/')[-1],
            output_format="png"
        )
        print("   ✓ Image edited successfully")
    except Exception as e:
        print(f"   ✗ Failed to edit image: {e}")
        return False

    # Display results
    print(f"\n4. Results:")
    print(f"   Seed: {result.get('seed')}")
    print(f"   Generated images: {len(result.get('images', []))}")

    if result.get('images'):
        for i, img in enumerate(result['images'], 1):
            print(f"\n   Image {i}:")
            print(f"   - URL: {img.get('url')}")
            print(f"   - Size: {img.get('width')}x{img.get('height')}")
            print(f"   - Format: {img.get('content_type')}")

    print("\n" + "="*60)
    print("✓ Integration test PASSED")
    print("="*60)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_integration.py <image_path> [prompt]")
        print("Example: python test_integration.py ~/Downloads/hannahai.png \"add a sunset background\"")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "add a sunset background"

    success = test_fal_integration(image_path, prompt)
    sys.exit(0 if success else 1)
