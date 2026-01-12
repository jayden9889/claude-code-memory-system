"""
Transcribe Instagram video/reel using yt-dlp with auto-captions or manual listening.
Falls back to downloading video and providing instructions for manual transcription.
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


def download_with_subtitles(url, output_path):
    """
    Try to download Instagram video with auto-generated subtitles.

    Args:
        url (str): Instagram post/reel URL
        output_path (str): Path to save video

    Returns:
        tuple: (video_path, subtitle_path)
    """
    try:
        print(f"📥 Attempting to download with auto-generated subtitles...")

        # Find yt-dlp executable
        import shutil
        yt_dlp_path = shutil.which('yt-dlp')
        if not yt_dlp_path:
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
                raise FileNotFoundError("yt-dlp not found")

        # Try to download with subtitles
        cmd = [
            yt_dlp_path,
            '--write-auto-subs',
            '--sub-lang', 'en',
            '--convert-subs', 'srt',
            '--skip-download',  # Only get subtitles
            '-o', output_path,
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check if subtitle file was created
        base_path = Path(output_path)
        subtitle_files = list(base_path.parent.glob(f"{base_path.stem}*.srt"))

        if subtitle_files and result.returncode == 0:
            log_success("Downloaded auto-generated subtitles")
            return None, str(subtitle_files[0])
        else:
            print("⚠️  No auto-generated subtitles available")
            return None, None

    except Exception as e:
        print(f"⚠️  Could not get auto-subtitles: {e}")
        return None, None


def parse_subtitles(subtitle_file):
    """
    Parse SRT subtitle file and extract text.

    Args:
        subtitle_file (str): Path to SRT file

    Returns:
        str: Extracted text
    """
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple SRT parsing - extract lines that don't contain timestamps or numbers
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            # Skip empty lines, numbers, and timestamp lines
            if line and not line.isdigit() and '-->' not in line:
                lines.append(line)

        return ' '.join(lines)

    except Exception as e:
        log_error(f"Failed to parse subtitles: {e}")
        return None


def download_video_info(url):
    """
    Get video information using yt-dlp.

    Args:
        url (str): Instagram URL

    Returns:
        dict: Video information
    """
    try:
        import shutil
        yt_dlp_path = shutil.which('yt-dlp')
        if not yt_dlp_path:
            possible_paths = [
                '/Users/jaydenmortimer/Library/Python/3.9/bin/yt-dlp',
                os.path.expanduser('~/Library/Python/3.9/bin/yt-dlp'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    yt_dlp_path = path
                    break

        cmd = [
            yt_dlp_path,
            '--dump-json',
            '--no-playlist',
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)

        return info

    except Exception as e:
        log_error(f"Could not get video info: {e}")
        return None


def extract_video_id(url):
    """Extract ID from Instagram URL."""
    parts = url.rstrip('/').split('/')
    if 'p' in parts or 'reel' in parts:
        try:
            idx = parts.index('p') if 'p' in parts else parts.index('reel')
            return parts[idx + 1]
        except (IndexError, ValueError):
            pass
    return parts[-1] if parts else 'instagram_video'


def main(url):
    """
    Main function - attempt to get transcript via multiple methods.

    Args:
        url (str): Instagram URL
    """
    try:
        # Create .tmp directory
        tmp_dir = Path('.tmp')
        tmp_dir.mkdir(exist_ok=True)

        video_id = extract_video_id(url)
        output_base = str(tmp_dir / f"instagram_{video_id}")

        print(f"\n{'='*60}")
        print(f"INSTAGRAM VIDEO TRANSCRIPTION")
        print(f"{'='*60}\n")
        print(f"Video ID: {video_id}")
        print(f"URL: {url}\n")

        # Method 1: Try to get auto-generated subtitles
        print("METHOD 1: Checking for auto-generated subtitles...")
        video_path, subtitle_path = download_with_subtitles(url, output_base)

        if subtitle_path:
            transcript = parse_subtitles(subtitle_path)
            if transcript:
                # Save transcript
                transcript_file = str(tmp_dir / f"transcript_instagram_{video_id}.txt")
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)

                print(f"\n{'='*60}")
                print(f"✓ TRANSCRIPTION COMPLETE (via auto-subtitles)")
                print(f"{'='*60}\n")
                print(f"📄 Saved to: {transcript_file}\n")
                print(f"{'='*60}")
                print(f"TRANSCRIPT:")
                print(f"{'='*60}\n")
                print(transcript)
                print(f"\n{'='*60}\n")

                return transcript

        # Method 2: Get video info and description
        print("\nMETHOD 2: Extracting video metadata...")
        info = download_video_info(url)

        if info:
            description = info.get('description', '')
            if description:
                print(f"\n{'='*60}")
                print(f"VIDEO DESCRIPTION:")
                print(f"{'='*60}\n")
                print(description)
                print(f"\n{'='*60}\n")

        # Method 3: Provide manual transcription instructions
        print("\nMETHOD 3: Manual transcription required")
        print(f"\n{'='*60}")
        print("MANUAL TRANSCRIPTION INSTRUCTIONS")
        print(f"{'='*60}\n")
        print("Since auto-subtitles are not available, please:")
        print(f"\n1. Open the video in your browser:")
        print(f"   {url}")
        print(f"\n2. Watch the video and transcribe the audio")
        print(f"\n3. Save the transcript to:")
        print(f"   .tmp/transcript_instagram_{video_id}.txt")
        print(f"\n{'='*60}\n")

        # Alternative: Suggest using web-based transcription services
        print("ALTERNATIVE OPTIONS:")
        print("-" * 60)
        print("1. Use a web-based transcription service:")
        print("   - Otter.ai")
        print("   - Rev.com")
        print("   - Descript")
        print("   - Trint")
        print("\n2. Use browser extensions:")
        print("   - Read Aloud")
        print("   - Voice In")
        print("\n3. Use mobile apps with audio recording")
        print(f"{'='*60}\n")

        return None

    except Exception as e:
        log_error(f"Process failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_instagram_simple.py <instagram_url>")
        print("Example: python transcribe_instagram_simple.py https://www.instagram.com/p/DTO6HfSjTnE/")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
