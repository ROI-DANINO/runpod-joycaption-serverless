#!/usr/bin/env python3
"""
Check RunPod endpoint status and configuration
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")

print("=" * 70)
print("RunPod Endpoint Diagnostics")
print("=" * 70)
print(f"API Key: {RUNPOD_API_KEY[:20]}...{RUNPOD_API_KEY[-4:]}")
print(f"Endpoint ID: {ENDPOINT_ID}")
print()

# Try different API endpoints to diagnose
tests = [
    ("Health Check", f"https://api.runpod.ai/v2/{ENDPOINT_ID}/health"),
    ("Status", f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status"),
    ("Run Sync", f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"),
]

headers = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json"
}

for name, url in tests:
    print(f"\nTesting: {name}")
    print(f"URL: {url}")

    try:
        # GET request
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  GET Status: {response.status_code}")
        if response.text:
            print(f"  Response: {response.text[:200]}")

    except Exception as e:
        print(f"  GET Error: {e}")

    # Also try POST for runsync
    if "runsync" in url:
        try:
            response = requests.post(
                url,
                json={"input": {}},
                headers=headers,
                timeout=10
            )
            print(f"  POST Status: {response.status_code}")
            if response.text:
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  POST Error: {e}")

print("\n" + "=" * 70)
print("Next steps:")
print("=" * 70)
print("1. Check RunPod console: https://www.runpod.io/console/serverless")
print("2. Verify endpoint is 'Active' (not 'Deploying' or 'Error')")
print("3. Check endpoint logs for errors")
print("4. Ensure your API key has 'Serverless' permissions")
print("5. Try regenerating API key if needed")
