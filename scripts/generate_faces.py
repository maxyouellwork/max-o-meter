#!/usr/bin/env python3
"""Generate the 8 Max-O-Meter face collectables via Gemini Nano Banana."""
import os
import sys
from pathlib import Path
from google import genai
from google.genai import types

PROJECT = Path(__file__).resolve().parent.parent
REFERENCE = PROJECT / "reference.webp"
OUT_DIR = PROJECT / "images"
OUT_DIR.mkdir(exist_ok=True)

# Load API key from keys.env
keys_path = Path.home() / ".claude" / "keys.env"
for line in keys_path.read_text().splitlines():
    if line.startswith("GOOGLE_API_KEY="):
        os.environ["GOOGLE_API_KEY"] = line.split("=", 1)[1].strip()

client = genai.Client()

STYLE = (
    "Photorealistic tight chest-up portrait, head centred, looking directly at camera, "
    "studio softbox lighting with soft rim light, sharp focus, magazine cover quality, "
    "1:1 square aspect ratio. Keep the same person from the reference photo — "
    "match the exact face, hair, and features precisely."
)

CARDS = [
    ("face-001", "teal blue gradient",
     "smug satisfied half-smile, one eyebrow slightly raised, eyes glinting with mischief, head tilted ever so slightly to the side, casual relaxed posture"),
    ("face-010", "warm sage green gradient",
     "playful lopsided smirk, lips pressed together suppressing a laugh, eyes bright and amused, slight shoulder shrug"),
    ("face-025", "mustard yellow gradient",
     "mid-wink with one eye closed and the other looking at camera, big cheeky grin showing teeth, finger guns pointed loosely toward the lens"),
    ("face-050", "burnt orange gradient",
     "single sharply raised eyebrow, lips slightly pursed in a flat unimpressed expression, slight head tilt of disbelief, arms folded"),
    ("face-100", "deep crimson red gradient",
     "wide devilish grin showing teeth, eyes narrowed mischievously, slight forward lean toward the camera, hands steepled in front like a cartoon villain, dramatic side shadow"),
    ("face-250", "electric purple gradient",
     "head thrown back mid-laugh with mouth wide open in a maniacal cackle, eyes squeezed shut with delight, hands raised triumphantly near the face, pure unhinged joy, dramatic uplight"),
    ("face-500", "soft cream and gold gradient",
     "the most innocent wide-eyed angelic expression, soft serene smile, hands clasped together in front like a choirboy, a subtle glowing golden halo floating above the head, soft heavenly light from above"),
    ("face-1000", "acid green gradient",
     "completely unhinged wide-eyed chaotic expression, manic grin stretching ear to ear, hair slightly dishevelled, hands clutching the sides of the head, full goblin energy, hard contrasty shadows"),
]

reference_bytes = REFERENCE.read_bytes()
reference_part = types.Part.from_bytes(data=reference_bytes, mime_type="image/webp")

for name, bg, expression in CARDS:
    out_path = OUT_DIR / f"{name}.png"
    if out_path.exists():
        print(f"  skip {name} (exists)")
        continue
    prompt = (
        f"Using the person in the reference photo, generate a portrait showing them with: {expression}. "
        f"Background: solid {bg}. {STYLE}"
    )
    print(f"  generating {name}...")
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[reference_part, prompt],
        )
        saved = False
        for part in response.candidates[0].content.parts:
            if getattr(part, "inline_data", None) and part.inline_data.data:
                out_path.write_bytes(part.inline_data.data)
                size_kb = len(part.inline_data.data) / 1024
                print(f"    saved {out_path.name} ({size_kb:.0f} KB)")
                saved = True
                break
        if not saved:
            print(f"    FAILED — no image in response. text: {response.text[:200] if hasattr(response,'text') else '?'}")
    except Exception as e:
        print(f"    ERROR: {e}")

print("\nDone.")
