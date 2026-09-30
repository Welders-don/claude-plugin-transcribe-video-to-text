# Transcribe Video to Text (Claude plugin)

Paste a video link into Claude and get a clean, readable transcript. Works with YouTube and any other site [yt-dlp](https://github.com/yt-dlp/yt-dlp) can read captions from (Vimeo, TED, Dailymotion and more).

## What it does

- Downloads only the caption track, never the video or audio.
- Removes the rolling repeats of YouTube auto captions, so every line appears once.
- Joins words into paragraphs, with optional `[mm:ss]` timestamps.
- Warns when a caption track is mostly `[Music]` or a few repeated words instead of speech, so Claude does not summarize noise.
- Prefers manual subtitles, then the original-language auto track, and says when it falls back to a machine-translated track.

Then ask for what you need: the full text, a summary, quotes with timestamps, notes or a translation.

## Install

In Claude Code:

```
/plugin marketplace add Welders-don/claude-plugin-transcribe-video-to-text
/plugin install transcribe-video-to-text@devexthub
```

## Requirements

- Python 3 (standard library only).
- yt-dlp (`pip install -U yt-dlp`). Claude asks before installing anything.

## Examples

> Get me the transcript of https://www.youtube.com/watch?v=arj7oStGLkU with timestamps and list the main points.

```
[00:12] so in college I was a government major which means I had to write a lot of papers ...
[00:43] come along and then I would kind of do this and that would happen every single paper ...
-- 11640 chars over 13:47, 14.1 chars/sec
```

> Save the German subtitles of this Vimeo talk as a text file without timestamps: https://vimeo.com/VIDEO_ID

> Find every place in this lecture where the speaker talks about pricing and quote it with timestamps: https://www.youtube.com/watch?v=VIDEO_ID

## Limits

- It reads existing captions. Videos without any captions need real speech recognition, which this plugin does not do.
- YouTube rate-limits VPN, cloud and CI IP addresses (HTTP 429 or "confirm you're not a bot"). Retry later or let yt-dlp use your browser session with `--cookies-from-browser`.

## Privacy

No API keys, no telemetry. The only network requests go to the video site through yt-dlp. The caption file stays in a temp folder on your machine.

## In the browser

For videos without captions, or when you are not in Claude, the [Transcribe Video to Text](https://www.devexthub.com/transcribe-video-to-text/) Chrome extension transcribes the audio of the tab you are watching.

## Support

Questions and bug reports: [GitHub Issues](https://github.com/Welders-don/claude-plugin-transcribe-video-to-text/issues).

## License

MIT
