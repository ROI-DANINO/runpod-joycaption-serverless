#!/usr/bin/env python3
"""
Test RunPod endpoint using async /run endpoint
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

load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")
TEST_DIR = Path("~/works_tation/claude/runpod-captioner/test_images/").expanduser()

# Try async endpoint
RUN_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
STATUS_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def find_first_image(directory: Path) -> Path:
    """Find the first image."""
    for file in directory.iterdir():
        if file.suffix.lower() in IMAGE_EXTENSIONS:
            return file
    print(f"ERROR: No images found in {directory}")
    sys.exit(1)


def encode_image_to_base64(image_path: Path) -> str:
    """Convert image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


print("=" * 70)
print("Testing RunPod Async Endpoint")
print("=" * 70)

# Find test image
image_path = find_first_image(TEST_DIR)
print(f"Test image: {image_path.name}")

# Encode
print("Encoding image...")
image_b64 = encode_image_to_base64(image_path)

# Prepare request
headers = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "input": {
        "image": image_b64
    }
}

# Submit job
print(f"\nSubmitting job to: {RUN_URL}")
try:
    response = requests.post(RUN_URL, json=payload, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        job_id = data.get("id")

        if job_id:
            print(f"\nJob ID: {job_id}")
            print("Polling for results...")

            # Poll for results
            for i in range(60):  # Poll for up to 60 seconds
                time.sleep(1)

                status_response = requests.get(
                    f"{STATUS_URL}{job_id}",
                    headers=headers,
                    timeout=10
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")

                    print(f"  [{i+1}s] Status: {status}")

                    if status == "COMPLETED":
                        caption = status_data.get("output", {}).get("caption")
                        print("\n" + "=" * 70)
                        print("SUCCESS!")
                        print("=" * 70)
                        print(f"Caption: {caption}")
                        sys.exit(0)

                    elif status == "FAILED":
                        error = status_data.get("error")
                        print(f"\nERROR: Job failed - {error}")
                        print(f"Full response: {json.dumps(status_data, indent=2)}")
                        sys.exit(1)

            print("\nTIMEOUT: Job did not complete in 60 seconds")
            sys.exit(1)

    else:
        print(f"ERROR: Failed to submit job")
        sys.exit(1)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
