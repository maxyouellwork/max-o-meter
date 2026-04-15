#!/usr/bin/env python3
"""Generate the 8 milestone voice lines via Modal Qwen3-TTS using Maxy's voice."""
import base64
import os
import subprocess
import sys
from pathlib import Path

import modal

PROJECT = Path(__file__).resolve().parent.parent
REF_AUDIO = PROJECT / "audio" / "maxy_ref.wav"
OUT_DIR = PROJECT / "audio"

REF_TEXT = (
    "this is me talking I'll read this while you sort that I'll start "
    "building the non voice fun stuff confetti combo system easter eggs "
    "web audio tap sounds"
)

# Per modal-tts.md tips:
# - end with periods not questions, append "mate" to prevent cutoff
# - use "pfft" for sniggers, avoid "haha"
# - ellipses create natural pauses
LINES = [
    ("voice-001", "Pfft... first offence, bro. Here we go."),
    ("voice-010", "Ooh, double digits already. Cute."),
    ("voice-025", "Twenty-five. I'm a prolific menace, me."),
    ("voice-050", "Fifty! Sis, have you considered blocking me."),
    ("voice-100", "Ohhh. One hundred. Certified menace."),
    ("voice-250", "Hahaha. Two hundred and fifty. Pure carnage."),
    ("voice-500", "Five hundred? Who, me. Couldn't be, girl."),
    ("voice-1000", "One thousand. It's a lifestyle now."),
]


def main():
    OUT_DIR.mkdir(exist_ok=True)
    ref_b64 = base64.b64encode(REF_AUDIO.read_bytes()).decode()
    TTSService = modal.Cls.from_name("qwen3-tts", "TTSService")
    svc = TTSService()

    for name, text in LINES:
        out_wav = OUT_DIR / f"{name}.wav"
        out_mp3 = OUT_DIR / f"{name}.mp3"
        if out_mp3.exists():
            print(f"  skip {name}")
            continue
        print(f"  generating {name}: \"{text}\"")
        try:
            wav_bytes = svc.generate.remote(
                text=text,
                seed=7,
                temperature=1.15,
                top_k=50,
                top_p=0.97,
                ref_audio_b64=ref_b64,
                ref_text=REF_TEXT,
            )
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

        out_wav.write_bytes(wav_bytes)

        # Trim leading silence and convert to MP3 for web
        trimmed = OUT_DIR / f"{name}_trimmed.wav"
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
        size_kb = out_mp3.stat().st_size / 1024
        print(f"    saved {out_mp3.name} ({size_kb:.0f} KB)")

    print("\nDone.")


if __name__ == "__main__":
    main()
