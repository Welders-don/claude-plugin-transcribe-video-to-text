#!/usr/bin/env python3
"""Turn a caption file (YouTube json3, WebVTT or SRT) into clean readable text.

Auto-generated captions repeat every line two or three times as they scroll
("rolling" captions). This script removes those repeats, strips styling tags,
joins the words into paragraphs and optionally prefixes each paragraph with a
[mm:ss] timestamp.

It also reports caption density (characters per second of video). Real speech
gives roughly 8-15 chars/sec; below 4 usually means the track is music tags,
"[Applause]" or a few repeated words, not a transcript.

Standard library only. Usage:
    python3 captions_to_text.py FILE [--timestamps] [--paragraph-seconds 30]
"""
import argparse
import html
import json
import re
import signal
import sys

TAG_RE = re.compile(r"<[^>]+>")
TIME_RE = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{3})")
LOW_DENSITY = 4.0


def parse_time(text):
    m = TIME_RE.search(text)
    if not m:
        return None
    h, mnt, s, ms = m.groups()
    return int(h or 0) * 3600 + int(mnt) * 60 + int(s) + int(ms) / 1000


def clean(text):
    text = html.unescape(TAG_RE.sub("", text))
    return re.sub(r"\s+", " ", text).strip()


def read_json3(raw):
    data = json.loads(raw)
    cues = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        text = clean("".join(s.get("utf8", "") for s in segs))
        if text:
            cues.append((ev.get("tStartMs", 0) / 1000, text))
    return cues


def read_vtt_srt(raw):
    cues = []
    for block in re.split(r"\n\s*\n", raw.replace("\r", "")):
        lines = [l for l in block.split("\n") if l.strip()]
        idx = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if idx is None:
            continue
        start = parse_time(lines[idx].split("-->")[0])
        if start is None:
            continue
        # one cue per line: rolling captions repeat whole lines, not fragments
        for line in lines[idx + 1:]:
            text = clean(line)
            if text:
                cues.append((start, text))
    return cues


def dedupe(cues):
    """Drop rolling-caption repeats: auto captions show each line two or three
    times as it scrolls. A line equal to one of the last two kept lines is a
    repeat; anything else is kept as is, so real repeated words survive."""
    out = []
    for start, text in cues:
        if any(text == t for _, t in out[-2:]):
            continue
        out.append((start, text))
    return out


def to_paragraphs(cues, seconds):
    paras = []
    for start, text in cues:
        if not paras or start - paras[-1][0] >= seconds:
            paras.append([start, text])
        else:
            paras[-1][1] += " " + text
    return paras


def stamp(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    return f"{h}:{rem // 60:02d}:{rem % 60:02d}" if h else f"{rem // 60:02d}:{rem % 60:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--timestamps", action="store_true", help="prefix paragraphs with [mm:ss]")
    ap.add_argument("--paragraph-seconds", type=float, default=30)
    args = ap.parse_args()

    raw = open(args.file, encoding="utf-8", errors="replace").read()
    cues = read_json3(raw) if raw.lstrip().startswith("{") else read_vtt_srt(raw)
    if not cues:
        sys.exit("No captions found in file.")
    span = max(cues[-1][0] - cues[0][0], 1)
    cues = dedupe(cues)

    for start, text in to_paragraphs(cues, args.paragraph_seconds):
        print(f"[{stamp(start)}] {text}\n" if args.timestamps else f"{text}\n")

    chars = sum(len(t) for _, t in cues)
    density = chars / span
    note = "  LOW: likely music/sound tags, not speech" if density < LOW_DENSITY else ""
    print(f"-- {chars} chars over {stamp(span)}, {density:.1f} chars/sec{note}", file=sys.stderr)


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):  # quiet exit when piped to head; absent on Windows
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
