#!/usr/bin/env python3
"""
RunPod JoyCaption Client
Generates captions for images without existing .txt files
"""

import os
import sys
import base64
import time
from pathlib import Path
from typing import List, Tuple

import requests
from dotenv import load_dotenv
from PIL import Image
from tqdm import tqdm

# Load environment variables
load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")

if not RUNPOD_API_KEY or not ENDPOINT_ID:
    print("ERROR: Missing RUNPOD_API_KEY or ENDPOINT_ID in .env")
    sys.exit(1)

# Configuration
API_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"
TARGET_DIR = "/mnt/c/Users/roi12/OneDrive/Desktop/alexandra/"
CAPTION_PREFIX = "ALX1, a woman named Alexandra, "
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def find_images_without_captions(directory: str) -> List[Path]:
    """Find all images that don't have corresponding .txt files."""
    directory = Path(directory)
    if not directory.exists():
        print(f"ERROR: Directory not found: {directory}")
        sys.exit(1)

    images_without_captions = []

    for file in directory.iterdir():
        if file.suffix.lower() in IMAGE_EXTENSIONS:
            txt_file = file.with_suffix(".txt")
            if not txt_file.exists():
                images_without_captions.append(file)

    return sorted(images_without_captions)


def encode_image_to_base64(image_path: Path) -> str:
    """Convert image to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_caption(image_path: Path) -> Tuple[bool, str]:
    """
    Generate caption for image via RunPod API.

    Returns:
        (success: bool, caption: str or error_message: str)
    """
    try:
        # Encode image
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

        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(API_URL, json=payload, headers=headers, timeout=120)

                if response.status_code == 200:
                    data = response.json()

                    # Check for errors in response
                    if data.get("status") == "FAILED":
                        return False, f"API error: {data.get('error', 'Unknown error')}"

                    # Extract caption
                    caption = data.get("output", {}).get("caption")
                    if caption:
                        return True, caption
                    else:
                        return False, "No caption in response"

                elif response.status_code == 503:
                    # Service unavailable, retry
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    return False, "Service unavailable after retries"

                else:
                    return False, f"HTTP {response.status_code}: {response.text}"

            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, "Request timeout after retries"

            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, f"Request error: {str(e)}"

        return False, "Max retries exceeded"

    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def save_caption(image_path: Path, caption: str):
    """Save caption to .txt file with prefix."""
    txt_path = image_path.with_suffix(".txt")
    full_caption = CAPTION_PREFIX + caption

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(full_caption)


def main():
    print("=" * 60)
    print("RunPod JoyCaption Client")
    print("=" * 60)
    print(f"Target directory: {TARGET_DIR}")
    print(f"Endpoint ID: {ENDPOINT_ID}")
    print()

    # Find images
    print("Scanning for images without captions...")
    images = find_images_without_captions(TARGET_DIR)

    if not images:
        print("No images found that need captions.")
        return

    print(f"Found {len(images)} images to caption\n")

    # Process images
    successful = 0
    failed = 0
    failed_files = []

    with tqdm(total=len(images), desc="Generating captions", unit="img") as pbar:
        for image_path in images:
            pbar.set_postfix({"file": image_path.name})

            success, result = generate_caption(image_path)

            if success:
                save_caption(image_path, result)
                successful += 1
            else:
                failed += 1
                failed_files.append((image_path.name, result))
                tqdm.write(f"FAILED: {image_path.name} - {result}")

            pbar.update(1)

    # Summary report
    print("\n" + "=" * 60)
    print("SUMMARY REPORT")
    print("=" * 60)
    print(f"Total images processed: {len(images)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed_files:
        print("\nFailed files:")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")

    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
