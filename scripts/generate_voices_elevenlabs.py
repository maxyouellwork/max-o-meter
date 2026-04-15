#!/usr/bin/env python3
"""Generate 8 milestone voice lines via ElevenLabs IVC (Instant Voice Clone)."""
import os
import sys
from pathlib import Path
import requests

PROJECT = Path(__file__).resolve().parent.parent
REF_AUDIO = PROJECT / "audio" / "maxy_ref_full.wav"
OUT_DIR = PROJECT / "audio"

# Load API key
keys_path = Path.home() / ".claude" / "keys.env"
api_key = None
for line in keys_path.read_text().splitlines():
    if line.startswith("ELEVENLABS_API_KEY="):
        api_key = line.split("=", 1)[1].strip()
        break
if not api_key:
    print("ELEVENLABS_API_KEY missing")
    sys.exit(1)

HEADERS = {"xi-api-key": api_key}
BASE = "https://api.elevenlabs.io/v1"

LINES = [
    ("voice-001", "First offence... it begins."),
    ("voice-010", "Pfft. Double digits already."),
    ("voice-025", "Twenty five. I'm prolific, me."),
    ("voice-050", "Josh... have you considered blocking me?"),
    ("voice-100", "One hundred. Certified menace."),
    ("voice-250", "Two hundred and fifty. Hahahaha."),
    ("voice-500", "Five hundred? Who, me? I'm an angel."),
    ("voice-1000", "One thousand. It's a lifestyle now."),
]

VOICE_NAME = "Maxy_MaxOMeter"

def find_existing_voice():
    r = requests.get(f"{BASE}/voices", headers=HEADERS)
    r.raise_for_status()
    for v in r.json().get("voices", []):
        if v.get("name") == VOICE_NAME:
            return v["voice_id"]
    return None

def create_voice():
    print(f"  creating IVC voice '{VOICE_NAME}' from {REF_AUDIO.name}...")
    with open(REF_AUDIO, "rb") as f:
        files = {"files": (REF_AUDIO.name, f, "audio/wav")}
        data = {"name": VOICE_NAME, "description": "Max for Max-O-Meter joke app"}
        r = requests.post(f"{BASE}/voices/add", headers=HEADERS, files=files, data=data)
    if r.status_code >= 400:
        print(f"    ERROR creating voice: {r.status_code} {r.text}")
        sys.exit(1)
    voice_id = r.json()["voice_id"]
    print(f"    voice_id: {voice_id}")
    return voice_id

def generate_one(voice_id, name, text):
    out_path = OUT_DIR / f"{name}.mp3"
    print(f"  {name}: {text!r}")
    body = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.35,
            "similarity_boost": 0.85,
            "style": 0.6,
            "use_speaker_boost": True,
        },
    }
    r = requests.post(
        f"{BASE}/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        headers={**HEADERS, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        json=body,
    )
    if r.status_code >= 400:
        print(f"    ERROR: {r.status_code} {r.text[:300]}")
        return False
    out_path.write_bytes(r.content)
    print(f"    saved {out_path.name} ({len(r.content)/1024:.0f} KB)")
    return True

def main():
    OUT_DIR.mkdir(exist_ok=True)
    voice_id = find_existing_voice()
    if voice_id:
        print(f"  reusing existing voice {voice_id}")
    else:
        voice_id = create_voice()

    for name, text in LINES:
        generate_one(voice_id, name, text)

    print("\nDone.")

if __name__ == "__main__":
    main()
