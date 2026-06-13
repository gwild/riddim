#!/usr/bin/env python3
"""Curate sample packs for the EP-40 Riddim.

Converts curated audio to the EP-40's native format (46875 Hz, 16-bit, mono)
via ffmpeg for maximum storage efficiency, writing each pack into
ep40-packs/<pack>/ with clean sequential names. Load a pack folder through the
EP Sample Tool (teenage.engineering/apps/ep-sample-tool).
"""

import os
import re
import shutil
import subprocess
import sys
import wave

# Prefer the self-contained static ffmpeg in .tools (Homebrew's ffmpeg has a
# broken dylib chain on this OS); fall back to PATH ffmpeg if absent.
_LOCAL_FFMPEG = os.path.join(os.path.dirname(__file__), ".tools", "ffmpeg")
FFMPEG = _LOCAL_FFMPEG if os.path.isfile(_LOCAL_FFMPEG) else "ffmpeg"

# EP-40 native sampling format.
RATE = 46875
CHANNELS = 1          # mono — halves size vs stereo
BITS = "s16"

BITWIG = ("/Users/gregorywildes/Library/Application Support/Bitwig/"
          "Bitwig Studio/installed-packages/1.0/samples")
MOLDOVER = "/Users/gregorywildes/Downloads/(!)_Moldover_-_Molded_Breaks/Samples/Imported"
OUT_ROOT = "/Users/gregorywildes/riddim/ep40-packs"

# EP-40 caps: 999 slots, 128 MB total per loaded set.
MAX_BYTES = 128 * 1024 * 1024

LEGEND_808 = f"{BITWIG}/Bitwig/Classic Drum Machines/Legend 808"

# Each pack has one or more sources; a source is selected and named independently
# so a single pack can mix, e.g., loops and one-shots.
PACKS = [
    {"name": "01_808_kit", "sources": [
        {"roots": [LEGEND_808], "exclude": ["accent"], "cap": 64}]},
    {"name": "02_909_kit", "sources": [
        {"roots": [f"{BITWIG}/Bitwig/Classic Drum Machines/Legend 909"],
         "exclude": ["accent"], "cap": 64}]},
    {"name": "03_acoustic_drums", "sources": [
        {"roots": [f"{BITWIG}/Bitwig/Nektar's Acoustic Drums"], "cap": 64}]},
    {"name": "04_bass_and_synths", "sources": [
        {"roots": [f"{BITWIG}/Irrupt/Irrupt System/BASS",
                   f"{BITWIG}/Irrupt/Irrupt System/SYNTHS"], "cap": 64}]},
    {"name": "05_funk_breaks", "sources": [
        {"roots": [MOLDOVER], "cap": 20}]},
    # Loop kit: short Moldover breaks that loop as complete repeats, paired with
    # an 808 drum kit so you can layer live hits over the running loop.
    {"name": "06_break_kit", "sources": [
        {"roots": [MOLDOVER], "cap": 10, "max_sec": 12, "prefix": "loop"},
        {"roots": [LEGEND_808], "exclude": ["accent"], "cap": 24,
         "prefix": "drum"}]},
]


def duration(path):
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / w.getframerate()
    except (wave.Error, EOFError, OSError):
        return None


def collect(src):
    exclude = src.get("exclude", [])
    max_sec = src.get("max_sec")
    files = []
    for root in src["roots"]:
        for dirpath, _, names in os.walk(root):
            for n in names:
                if not n.lower().endswith((".wav", ".aif", ".aiff", ".flac")):
                    continue
                if any(x in n.lower() for x in exclude):
                    continue
                full = os.path.join(dirpath, n)
                if max_sec is not None:
                    d = duration(full)
                    if d is None or d > max_sec:
                        continue
                files.append(full)
    files.sort()
    return files


def even_spread(items, cap):
    """Pick up to `cap` items spread across the list, not just the first N."""
    if len(items) <= cap:
        return items
    step = len(items) / cap
    return [items[int(i * step)] for i in range(cap)]


def clean_name(path, idx, prefix):
    base = os.path.splitext(os.path.basename(path))[0]
    base = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_")
    tag = f"{prefix}_" if prefix else ""
    return f"{idx:02d}_{tag}{base[:40]}.wav"


def convert(src, dst):
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", src,
         "-ar", str(RATE), "-ac", str(CHANNELS), "-sample_fmt", BITS, dst],
        check=True)


def main():
    if FFMPEG == "ffmpeg" and not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH")
    if os.path.isdir(OUT_ROOT):
        for d, _, fs in os.walk(OUT_ROOT):
            for f in fs:
                os.chmod(os.path.join(d, f), 0o644)
        shutil.rmtree(OUT_ROOT)
    os.makedirs(OUT_ROOT)
    print(f"format: {RATE} Hz / 16-bit / {'mono' if CHANNELS == 1 else 'stereo'}\n")
    for pack in PACKS:
        out_dir = os.path.join(OUT_ROOT, pack["name"])
        os.makedirs(out_dir)
        idx = 0
        for src in pack["sources"]:
            chosen = even_spread(collect(src), src["cap"])
            for s in chosen:
                idx += 1
                convert(s, os.path.join(out_dir, clean_name(s, idx, src.get("prefix"))))
        files = os.listdir(out_dir)
        total = sum(os.path.getsize(os.path.join(out_dir, f)) for f in files)
        warn = "  ⚠ OVER 128 MB" if total > MAX_BYTES else ""
        print(f"{pack['name']}: {len(files)} samples, "
              f"{total / 1024 / 1024:.1f} MB{warn}")
    print(f"\ndone -> {OUT_ROOT}")


if __name__ == "__main__":
    main()
