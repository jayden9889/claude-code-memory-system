"""
Extract transcript from YouTube video.
Requires youtube-transcript-api package.
"""

import sys
import json
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    import youtube_transcript_api
    YouTubeTranscriptApi = youtube_transcript_api.YouTubeTranscriptApi

from utils import save_json, log_error, log_success


def extract_video_id(url):
    """
    Extract video ID from YouTube URL.

    Args:
        url (str): YouTube URL

    Returns:
        str: Video ID
    """
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    elif 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    else:
        return url


def get_transcript(video_id):
    """
    Get transcript for a YouTube video.

    Args:
        video_id (str): YouTube video ID

    Returns:
        str: Full transcript text
    """
    try:
        # Get transcript using the API instance
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)

        # Combine all text
        full_transcript = ' '.join([entry['text'] for entry in transcript_list])

        # Save raw transcript data
        save_json(transcript_list, f'transcript_{video_id}_raw.json')

        log_success(f"Retrieved transcript for video {video_id}",
                   {'entries': len(transcript_list),
                    'length': len(full_transcript)})

        return full_transcript

    except Exception as e:
        log_error(f"Failed to get transcript: {e}")
        raise


def main(url):
    """
    Extract and save transcript from YouTube URL.

    Args:
        url (str): YouTube video URL or ID
    """
    try:
        video_id = extract_video_id(url)
        print(f"Extracting transcript for video: {video_id}")

        transcript = get_transcript(video_id)

        # Save full transcript as text
        output_file = f'.tmp/transcript_{video_id}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcript)

        print(f"\n✓ Transcript saved to: {output_file}")
        print(f"✓ Length: {len(transcript)} characters")
        print(f"\nFirst 500 characters:\n{transcript[:500]}...")

        return transcript

    except Exception as e:
        log_error(f"Transcript extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_youtube_transcript.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
