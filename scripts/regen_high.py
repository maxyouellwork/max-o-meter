#!/usr/bin/env python3
"""Regenerate just the high-milestone voice lines with tighter params for voice consistency."""
import base64
import os
import subprocess
from pathlib import Path
import modal

PROJECT = Path(__file__).resolve().parent.parent
REF_AUDIO = PROJECT / "audio" / "maxy_ref.wav"
OUT_DIR = PROJECT / "audio"

REF_TEXT = (
    "is a test, testing the voice note to see if we get a good reference. "
    "It's more active and expressionist and it's a bit more exciting when "
    "recorded as it is now."
)

# Shorter text + multiple seed candidates per line.
# Tighter temp = better voice match, slight loss of expression.
LINES = [
    ("voice-100",  "One hundred. Certified menace.",       [7, 13, 42, 99, 1, 5]),
    ("voice-250",  "Two fifty. Pure carnage.",             [7, 13, 42, 99, 1, 5]),
    ("voice-500",  "Five hundred. Who, me. Couldn't be.",  [7, 13, 42, 99, 1, 5]),
    ("voice-1000", "One thousand. It's a lifestyle now.",  [7, 13, 42, 99, 1, 5]),
]

def main():
    ref_b64 = base64.b64encode(REF_AUDIO.read_bytes()).decode()
    TTSService = modal.Cls.from_name("qwen3-tts", "TTSService")
    svc = TTSService()

    for name, text, seeds in LINES:
        print(f"\n== {name}: {text!r}")
        for seed in seeds:
            out_wav = OUT_DIR / f"{name}_s{seed}.wav"
            out_mp3 = OUT_DIR / f"{name}_s{seed}.mp3"
            if out_mp3.exists():
                print(f"  skip seed {seed}")
                continue
            print(f"  seed {seed}...")
            try:
                wav_bytes = svc.generate.remote(
                    text=text,
                    seed=seed,
                    temperature=0.85,
                    top_k=20,
                    top_p=0.85,
                    ref_audio_b64=ref_b64,
                    ref_text=REF_TEXT,
                )
            except Exception as e:
                print(f"    ERROR: {e}")
                continue
            out_wav.write_bytes(wav_bytes)
            trimmed = OUT_DIR / f"{name}_s{seed}_t.wav"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(out_wav),
                "-af", "atrim=start=0.2,asetpts=PTS-STARTPTS,silenceremove=stop_periods=-1:stop_duration=0.6:stop_threshold=-40dB",
                "-ar", "24000", str(trimmed),
            ], capture_output=True)
            subprocess.run([
                "ffmpeg", "-y", "-i", str(trimmed),
                "-codec:a", "libmp3lame", "-b:a", "96k",
                str(out_mp3),
            ], capture_output=True)
            trimmed.unlink(missing_ok=True)
            out_wav.unlink(missing_ok=True)
            print(f"    saved {out_mp3.name} ({out_mp3.stat().st_size/1024:.0f} KB)")

    print("\nDone. Listen to candidates and pick the best for each:")
    for name, _, seeds in LINES:
        print(f"\n  {name}:")
        for seed in seeds:
            print(f"    afplay audio/{name}_s{seed}.mp3   # seed {seed}")

if __name__ == "__main__":
    main()
