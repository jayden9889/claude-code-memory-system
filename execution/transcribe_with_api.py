"""
Transcribe video using AssemblyAI cloud transcription API.
Requires ASSEMBLY_AI_API_KEY in .env file.
"""

import sys
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import log_error, log_success
except ImportError:
    def log_error(msg, details=None):
        print(f"❌ ERROR: {msg}")

    def log_success(msg, details=None):
        print(f"✓ {msg}")


def upload_file_to_assemblyai(file_path, api_key):
    """Upload video file to AssemblyAI."""
    print("📤 Uploading file to AssemblyAI...")

    url = "https://api.assemblyai.com/v2/upload"
    headers = {"authorization": api_key}

    with open(file_path, "rb") as f:
        response = requests.post(url, headers=headers, data=f)

    if response.status_code == 200:
        upload_url = response.json()["upload_url"]
        log_success(f"File uploaded")
        return upload_url
    else:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")


def start_transcription(audio_url, api_key):
    """Start transcription job."""
    print("🎤 Starting transcription...")

    url = "https://api.assemblyai.com/v2/transcript"
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    data = {
        "audio_url": audio_url
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        transcript_id = response.json()["id"]
        log_success(f"Transcription job started: {transcript_id}")
        return transcript_id
    else:
        raise Exception(f"Failed to start transcription: {response.status_code} - {response.text}")


def poll_transcription(transcript_id, api_key):
    """Poll for transcription completion."""
    url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {"authorization": api_key}

    print("⏳ Waiting for transcription to complete...")

    while True:
        response = requests.get(url, headers=headers)
        result = response.json()

        status = result["status"]

        if status == "completed":
            log_success("Transcription completed!")
            return result
        elif status == "error":
            raise Exception(f"Transcription failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   Status: {status}...")
            time.sleep(3)


def main(video_file):
    """
    Transcribe video using AssemblyAI.

    Args:
        video_file (str): Path to video file
    """
    try:
        # Get API key
        api_key = os.getenv("ASSEMBLY_AI_API_KEY")

        if not api_key:
            print("\n" + "="*60)
            print("ERROR: AssemblyAI API Key Not Found")
            print("="*60)
            print("\nTo use cloud transcription, you need to:")
            print("\n1. Sign up for AssemblyAI (free tier available):")
            print("   https://www.assemblyai.com/")
            print("\n2. Get your API key from the dashboard")
            print("\n3. Add it to your .env file:")
            print("   ASSEMBLY_AI_API_KEY=your_key_here")
            print("\n" + "="*60 + "\n")
            sys.exit(1)

        # Check if file exists
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file not found: {video_file}")

        print(f"\n{'='*60}")
        print(f"CLOUD-BASED VIDEO TRANSCRIPTION")
        print(f"{'='*60}\n")
        print(f"File: {video_file}")
        print(f"Size: {os.path.getsize(video_file) / (1024*1024):.2f} MB\n")

        # Upload file
        audio_url = upload_file_to_assemblyai(video_file, api_key)

        # Start transcription
        transcript_id = start_transcription(audio_url, api_key)

        # Poll for completion
        result = poll_transcription(transcript_id, api_key)

        # Extract transcript text
        transcript_text = result["text"]

        # Save to file
        video_path = Path(video_file)
        transcript_file = video_path.parent / f"transcript_{video_path.stem}.txt"

        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript_text)

        # Display results
        print(f"\n{'='*60}")
        print(f"TRANSCRIPTION COMPLETE")
        print(f"{'='*60}\n")
        print(f"📄 Saved to: {transcript_file}")
        print(f"📊 Word count: {len(transcript_text.split())}")
        print(f"📏 Character count: {len(transcript_text)}\n")
        print(f"{'='*60}")
        print(f"TRANSCRIPT:")
        print(f"{'='*60}\n")
        print(transcript_text)
        print(f"\n{'='*60}\n")

        return transcript_text

    except Exception as e:
        log_error(f"Transcription failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_with_api.py <video_file_path>")
        print("Example: python transcribe_with_api.py .tmp/instagram_DTO6HfSjTnE")
        sys.exit(1)

    video_file = sys.argv[1]
    main(video_file)
