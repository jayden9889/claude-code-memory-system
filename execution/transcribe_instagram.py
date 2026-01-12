"""
Transcribe Instagram video/reel using yt-dlp and OpenAI Whisper.
Downloads video, extracts audio, and transcribes using local Whisper model.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import log_error, log_success
except ImportError:
    def log_error(msg, details=None):
        print(f"❌ ERROR: {msg}")
        if details:
            print(f"   Details: {details}")

    def log_success(msg, details=None):
        print(f"✓ {msg}")
        if details:
            print(f"  Details: {details}")


def download_instagram_video(url, output_path):
    """
    Download Instagram video using yt-dlp.

    Args:
        url (str): Instagram post/reel URL
        output_path (str): Path to save video

    Returns:
        str: Path to downloaded video file
    """
    try:
        print(f"📥 Downloading Instagram video from: {url}")

        # Find yt-dlp executable
        import shutil
        yt_dlp_path = shutil.which('yt-dlp')
        if not yt_dlp_path:
            # Try common installation paths
            possible_paths = [
                '/Users/jaydenmortimer/Library/Python/3.9/bin/yt-dlp',
                os.path.expanduser('~/Library/Python/3.9/bin/yt-dlp'),
                '/usr/local/bin/yt-dlp',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    yt_dlp_path = path
                    break

            if not yt_dlp_path:
                raise FileNotFoundError("yt-dlp not found. Please install with: pip3 install yt-dlp")

        # Use yt-dlp to download the video
        cmd = [
            yt_dlp_path,
            '-f', 'best',  # Get best quality
            '-o', output_path,  # Output path
            '--no-playlist',  # Don't download playlists
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Check if file was downloaded (with or without extension)
        base_path = Path(output_path)

        # First check exact path
        if base_path.exists():
            log_success(f"Downloaded video to: {output_path}")
            return output_path

        # Then check with common video extensions
        possible_files = list(base_path.parent.glob(f"{base_path.name}.*"))

        if possible_files:
            actual_file = str(possible_files[0])
            log_success(f"Downloaded video to: {actual_file}")
            return actual_file
        else:
            raise FileNotFoundError(f"Could not find downloaded file matching {output_path}")

    except subprocess.CalledProcessError as e:
        log_error(f"Failed to download video: {e.stderr}")
        raise
    except Exception as e:
        log_error(f"Download failed: {str(e)}")
        raise


def transcribe_video(video_path):
    """
    Transcribe video using OpenAI Whisper.

    Args:
        video_path (str): Path to video file

    Returns:
        dict: Transcription result with text and segments
    """
    try:
        print(f"\n🎤 Transcribing video with Whisper...")

        import whisper

        # Load the model (base is a good balance of speed and accuracy)
        # Options: tiny, base, small, medium, large
        model = whisper.load_model("base")

        # Transcribe
        result = model.transcribe(video_path, verbose=True)

        log_success(f"Transcription complete", {
            'language': result.get('language', 'unknown'),
            'segments': len(result.get('segments', [])),
            'characters': len(result.get('text', ''))
        })

        return result

    except Exception as e:
        log_error(f"Transcription failed: {str(e)}")
        raise


def extract_video_id(url):
    """
    Extract a clean identifier from Instagram URL for file naming.

    Args:
        url (str): Instagram URL

    Returns:
        str: Clean identifier
    """
    # Extract the post ID from URL
    # URLs look like: https://www.instagram.com/p/DTO6HfSjTnE/ or /reel/...
    parts = url.rstrip('/').split('/')

    if 'p' in parts or 'reel' in parts:
        try:
            idx = parts.index('p') if 'p' in parts else parts.index('reel')
            return parts[idx + 1]
        except (IndexError, ValueError):
            pass

    # Fallback: use last part of URL
    return parts[-1] if parts else 'instagram_video'


def main(url):
    """
    Main function to download and transcribe Instagram video.

    Args:
        url (str): Instagram post/reel URL

    Returns:
        dict: Transcription results
    """
    try:
        # Create .tmp directory if it doesn't exist
        tmp_dir = Path('.tmp')
        tmp_dir.mkdir(exist_ok=True)

        # Extract video ID for file naming
        video_id = extract_video_id(url)

        # Set up file paths
        video_path = str(tmp_dir / f"instagram_{video_id}")
        transcript_txt = str(tmp_dir / f"transcript_instagram_{video_id}.txt")
        transcript_json = str(tmp_dir / f"transcript_instagram_{video_id}.json")

        print(f"Processing Instagram video: {video_id}\n")

        # Step 1: Download video
        downloaded_video = download_instagram_video(url, video_path)

        # Step 2: Transcribe
        result = transcribe_video(downloaded_video)

        # Step 3: Save results
        # Save full text
        with open(transcript_txt, 'w', encoding='utf-8') as f:
            f.write(result['text'])

        # Save detailed JSON with timestamps
        with open(transcript_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*60}")
        print(f"TRANSCRIPTION COMPLETE")
        print(f"{'='*60}")
        print(f"\n📄 Text saved to: {transcript_txt}")
        print(f"📄 JSON saved to: {transcript_json}")
        print(f"\n{'='*60}")
        print(f"TRANSCRIPT:")
        print(f"{'='*60}\n")
        print(result['text'])
        print(f"\n{'='*60}\n")

        # Clean up video file to save space
        try:
            os.remove(downloaded_video)
            print(f"🗑️  Cleaned up video file: {downloaded_video}")
        except Exception as e:
            print(f"⚠️  Could not delete video file: {e}")

        return result

    except Exception as e:
        log_error(f"Transcription process failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_instagram.py <instagram_url>")
        print("Example: python transcribe_instagram.py https://www.instagram.com/p/DTO6HfSjTnE/")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
