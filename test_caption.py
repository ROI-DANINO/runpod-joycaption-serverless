#!/usr/bin/env python3
"""
RunPod JoyCaption Test Script
Test endpoint with a single image and show verbose output
"""

import os
import sys
import base64
import time
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")

if not RUNPOD_API_KEY or not ENDPOINT_ID:
    print("ERROR: Missing RUNPOD_API_KEY or ENDPOINT_ID in .env")
    sys.exit(1)

# Configuration
API_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"
TEST_DIR = Path("~/works_tation/claude/runpod-captioner/test_images/").expanduser()
CAPTION_PREFIX = "ALX1, a woman named Alexandra, "

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def find_first_image(directory: Path) -> Path:
    """Find the first image in the test directory."""
    if not directory.exists():
        print(f"ERROR: Directory not found: {directory}")
        print("Creating test_images directory...")
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Please add test images to: {directory}")
        sys.exit(1)

    for file in directory.iterdir():
        if file.suffix.lower() in IMAGE_EXTENSIONS:
            return file

    print(f"ERROR: No images found in {directory}")
    print(f"Supported formats: {', '.join(IMAGE_EXTENSIONS)}")
    sys.exit(1)


def encode_image_to_base64(image_path: Path) -> str:
    """Convert image to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def test_caption(image_path: Path):
    """Test caption generation with verbose output."""
    print("=" * 70)
    print("RunPod JoyCaption - Endpoint Test")
    print("=" * 70)
    print(f"Endpoint URL: {API_URL}")
    print(f"Test image: {image_path.name}")
    print(f"Image size: {image_path.stat().st_size / 1024:.2f} KB")

    # Show image dimensions
    try:
        with Image.open(image_path) as img:
            print(f"Image dimensions: {img.size[0]}x{img.size[1]}")
    except Exception as e:
        print(f"Could not read image dimensions: {e}")

    print("-" * 70)

    # Encode image
    print("\nEncoding image to base64...")
    start_encode = time.time()
    try:
        image_b64 = encode_image_to_base64(image_path)
        encode_time = time.time() - start_encode
        print(f"Encoded in {encode_time:.2f}s (base64 length: {len(image_b64)} chars)")
    except Exception as e:
        print(f"ERROR encoding image: {e}")
        sys.exit(1)

    # Prepare request
    print("\nPreparing API request...")
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY[:20]}...{RUNPOD_API_KEY[-4:]}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "image": image_b64
        }
    }

    print(f"Headers: {json.dumps({k: v for k, v in headers.items()}, indent=2)}")
    print(f"Payload keys: {list(payload.keys())}")
    print(f"Input keys: {list(payload['input'].keys())}")

    # Send request
    print("\n" + "=" * 70)
    print("SENDING REQUEST TO RUNPOD...")
    print("=" * 70)

    start_request = time.time()

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=120
        )
        request_time = time.time() - start_request

        print(f"\nResponse received in {request_time:.2f}s")
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        print("\n" + "-" * 70)
        print("RAW RESPONSE:")
        print("-" * 70)
        print(response.text)

        if response.status_code == 200:
            print("\n" + "=" * 70)
            print("PARSED RESPONSE:")
            print("=" * 70)

            data = response.json()
            print(json.dumps(data, indent=2))

            # Extract caption
            status = data.get("status")
            print(f"\nJob status: {status}")

            if status == "COMPLETED":
                caption = data.get("output", {}).get("caption")

                if caption:
                    print("\n" + "=" * 70)
                    print("GENERATED CAPTION:")
                    print("=" * 70)
                    print(caption)

                    print("\n" + "=" * 70)
                    print("WITH PREFIX:")
                    print("=" * 70)
                    full_caption = CAPTION_PREFIX + caption
                    print(full_caption)

                    print("\n" + "=" * 70)
                    print("SUCCESS!")
                    print("=" * 70)
                    print(f"Caption length: {len(caption)} chars")
                    print(f"With prefix: {len(full_caption)} chars")
                    print(f"Total processing time: {request_time:.2f}s")

                else:
                    print("\nERROR: No caption found in response")
                    sys.exit(1)

            elif status == "FAILED":
                error = data.get("error", "Unknown error")
                print(f"\nERROR: Job failed - {error}")
                sys.exit(1)

            else:
                print(f"\nWARNING: Unexpected status - {status}")

        else:
            print(f"\nERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)

    except requests.exceptions.Timeout:
        print("\nERROR: Request timeout (>120s)")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Request failed - {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\nERROR: Unexpected error - {e}")
        sys.exit(1)


def main():
    # Find first test image
    image_path = find_first_image(TEST_DIR)

    # Test captioning
    test_caption(image_path)


if __name__ == "__main__":
    main()
