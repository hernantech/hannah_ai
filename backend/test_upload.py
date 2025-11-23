#!/usr/bin/env python3
"""
Test script for the /api/upload endpoint
Demonstrates how to send a base64 encoded image to the Flask API
"""

import requests
import base64
import json
import sys


def test_upload_base64_image(image_path=None, prompt="add a sunset background", api_url="http://localhost:5000/api/upload"):
    """
    Test the image upload endpoint with a base64 encoded image

    Args:
        image_path: Path to an image file (optional)
        prompt: AI editing prompt
        api_url: URL of the upload endpoint
    """

    if image_path:
        # Read and encode an actual image file
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                filename = image_path.split('/')[-1]
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return
    else:
        # Use a tiny 1x1 pixel PNG image as test data
        base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        filename = "test_pixel.png"

    # Prepare the payload
    payload = {
        "image": base64_image,
        "prompt": prompt,
        "filename": filename
    }

    print(f"Sending image to {api_url}...")
    print(f"Prompt: {prompt}")
    print(f"Image size: {len(base64_image)} bytes (base64 encoded)")

    try:
        # Send the request
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # Print the response
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to {api_url}")
        print("Make sure the Flask server is running!")
    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If an image path is provided as command line argument
        image_path = sys.argv[1]
        prompt = sys.argv[2] if len(sys.argv) > 2 else "add a sunset background"
        test_upload_base64_image(image_path, prompt)
    else:
        # Use test data
        print("No image path provided. Using test data...")
        test_upload_base64_image()
        print("\nTo test with your own image, run:")
        print("  python test_upload.py /path/to/your/image.jpg \"your prompt here\"")
