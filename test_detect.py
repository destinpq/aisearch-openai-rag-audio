#!/usr/bin/env python3
import requests
import json
import time
import sys

print("Testing detect_dialect endpoint...")

# Wait for server to start
time.sleep(5)

try:
    print("Sending request to detect-dialect endpoint...")
    response = requests.post('http://localhost:2355/detect-dialect',
                           json={'text': 'Hello world'},
                           timeout=10)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'Response: {result}')
        print("SUCCESS: detect_dialect endpoint is working!")
    else:
        print(f'Error response: {response.text}')
except requests.exceptions.ConnectionError as e:
    print(f'Connection Error: {e}')
    print("Make sure the server is running on port 2355")
except Exception as e:
    print(f'Error: {e}')

print("\n" + "="*50)
print("Testing TTS endpoint with auto-detection...")

try:
    print("Sending TTS request with auto-detection...")
    response = requests.post('http://localhost:2355/tts',
                           json={'text': 'Hello world', 'lang': 'auto'},
                           timeout=30)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        print(f'Response content length: {len(response.content)} bytes')
        print("SUCCESS: TTS endpoint with auto-detection is working!")
        # Save the audio to a file for verification
        with open('/tmp/test_tts_auto.mp3', 'wb') as f:
            f.write(response.content)
        print("Audio saved to /tmp/test_tts_auto.mp3")
    else:
        print(f'Error response: {response.text}')
except Exception as e:
    print(f'Error: {e}')

print("\n" + "="*50)
print("Testing TTS endpoint with Marathi text...")

try:
    print("Sending TTS request with Marathi text...")
    response = requests.post('http://localhost:2355/tts',
                           json={'text': 'नमस्ते दुनिया', 'lang': 'auto'},
                           timeout=30)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        print(f'Response content length: {len(response.content)} bytes')
        print("SUCCESS: TTS endpoint with Marathi auto-detection is working!")
        # Save the audio to a file for verification
        with open('/tmp/test_tts_marathi.mp3', 'wb') as f:
            f.write(response.content)
        print("Audio saved to /tmp/test_tts_marathi.mp3")
    else:
        print(f'Error response: {response.text}')
except Exception as e:
    print(f'Error: {e}')