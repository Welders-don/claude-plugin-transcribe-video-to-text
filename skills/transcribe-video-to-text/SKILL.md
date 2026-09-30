---
name: transcribe-video-to-text
description: Get a clean text transcript of a YouTube (or Vimeo, TED and other yt-dlp supported) video from its captions, without downloading the video. Use when the user shares a video link and asks for the transcript, the text, subtitles, quotes, notes or a summary of what is said in it.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/captions_to_text.py *)
---

# Transcribe video to text

Fetches the video's existing captions (manual or auto-generated) with yt-dlp and turns them into readable text: rolling repeats of auto captions removed, styling tags stripped, words joined into paragraphs, optional `[mm:ss]` timestamps. No audio is downloaded or sent anywhere.

## Steps

1. **Check that yt-dlp is available.** Use `yt-dlp` or `python3 -m yt_dlp`, whichever works. If neither is installed, ask the user before installing it (`pip install -U yt-dlp`). An outdated yt-dlp is the most common cause of failures on YouTube, so suggest updating if a fetch fails.

2. **See which caption tracks exist** (skip if the user already named a language):
   ```bash
   yt-dlp --list-subs --skip-download "URL"
   ```
   Prefer, in order: manual subtitles in the language the user wants, the original-language auto track (`<lang>-orig` on YouTube), then any auto track. Auto-translated tracks are machine translations of the auto captions, so mention that when you use one.

3. **Download only the captions** into a temp folder:
   ```bash
   yt-dlp --skip-download --write-subs --write-auto-subs \
     --sub-langs "LANG" --sub-format "json3/vtt/srt/best" \
     -o "%(id)s.%(ext)s" -P "CAPTIONS_DIR" "URL"
   ```
   Replace `LANG` with the track code, for example `en`, `en-orig` or `de`, and `CAPTIONS_DIR` with a fresh temp folder (for example from `mktemp -d`).

4. **Convert to text** with the bundled script:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/captions_to_text.py FILE --timestamps
   ```
   Drop `--timestamps` for plain text. `--paragraph-seconds N` changes paragraph length (default 30). The script prints a density line to stderr, for example `-- 11639 chars over 13:34, 14.3 chars/sec`.

5. **Check the density line before using the text.** Normal speech is about 8-15 chars/sec. If the script says `LOW`, the track is mostly `[Music]`, `[Applause]` or a few repeated words (common for songs and videos with little talking). Tell the user the captions do not contain a real transcript instead of summarizing them.

6. **Deliver.** Short transcripts can go straight into the reply. For long ones, save to a `.md` or `.txt` file in the working directory and tell the user the path. If the user asked for a summary, quotes or notes, work from the cleaned text and cite timestamps.

## When it does not work

- **No caption tracks at all**: this method cannot help, it reads captions and does not do speech recognition. Say so plainly. The user needs a speech-to-text tool for that video.
- **HTTP 429 / "Sign in to confirm you're not a bot"**: YouTube is rate-limiting the IP (typical on VPNs, cloud servers and CI). Wait and retry, or add `--cookies-from-browser chrome` (or firefox, edge, safari) so yt-dlp uses the user's own logged-in session. Ask before reading browser cookies.
- **Private, members-only or age-restricted videos**: need `--cookies-from-browser` as above.
- **Playlists**: add `--yes-playlist` and run the script on each file. Confirm with the user first if the playlist is long.
