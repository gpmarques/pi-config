---
name: youtube-transcript
description: Fetch the transcript and title of a YouTube video as JSON. Use when the user provides a YouTube URL and you need the spoken content (captions) for analysis, summarization, quoting, or search.
---

# YouTube Transcript

Fetches a YouTube video's title and full transcript by pulling captions via `yt-dlp`. Prefers manual English subtitles, falls back to auto-generated English.

## Requirements

- `yt-dlp` on PATH (`brew install yt-dlp`)
- Python 3

## Usage

```bash
python3 ~/.pi/agent/skills/youtube-transcript/fetch_transcript.py "<youtube_url>"
```

## Output

Prints a JSON object to stdout:

```json
{
  "title": "Video title",
  "transcript": "full transcript text as a single string"
}
```

Progress/info logs go to stderr. On failure (no English captions, network error, bad URL), the script exits non-zero with a message on stderr.

## Notes

- Only English captions are attempted (`en`, `en-US`, `en-GB`, then any `en*`). Manual captions are preferred over auto-generated.
- Transcript is plain text with timing/formatting stripped — not timestamped.
- Captionless videos and videos with only non-English caption tracks fail. The script does not transcribe speech or attempt non-English captions; a video in any spoken language works only when a usable English caption track exists.
- There is no built-in media-transcription fallback. A separately installed tool such as `pi-transcribe` can transcribe a downloaded local audio or video file through its `transcribe_file` tool, but that package is not bundled with or installed by this skill.
