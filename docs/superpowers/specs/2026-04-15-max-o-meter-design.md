# Max-O-Meter — Design

**Date:** 2026-04-15
**For:** Josh (the user/tapper). Max is the subject being tallied.

## Purpose

A silly single-page web app that lets Josh tap to tally every time Max has annoyed him. The count persists across sessions so the running total is never lost.

## Scope

- Single `index.html` file. Vanilla HTML/CSS/JS. No build step, no dependencies.
- Deployed to GitHub Pages (fastest path). Shareable URL for Josh.

## Features

### Core
- **Full-screen tap target.** Tapping anywhere on the page increments the tally by 1.
- **Huge centred number** showing the current count.
- **Title:** "Times Max Has Annoyed Josh"
- **Persistence.** Count stored in `localStorage` under a single key (e.g. `maxOMeterCount`). Survives refresh/close.

### Feedback on tap
- Bouncy scale-up animation on the number.
- Short screen shake.
- Haptic vibration on mobile (`navigator.vibrate(10)` — no-op elsewhere).

### Mood
- Background colour gradually shifts from calm blue → angry red as count climbs. Interpolate every tap; cap at ~500 for "fully red".
- A small emoji face near the bottom that changes at milestones: 😊 (0–9) → 🙂 (10–49) → 😏 (50–99) → 😒 (100–499) → 😈 (500–999) → 💀 (1000+).

### Milestone messages
Briefly pop up over the screen then fade (~2s). Fires only when the count first crosses the threshold.

- 1: "First offence. It begins."
- 10: "Double digits already, Max."
- 25: "Prolific."
- 50: "Josh, have you considered blocking him?"
- 100: "Certified menace."
- 250: "A quarter-millennium of Max."
- 500: "You are a saint, Josh."
- 1000: "At this point it's a lifestyle."

### Reset
- Tiny "↻" button fixed in a corner.
- Requires a **1-second long-press** to trigger reset (prevents accidents — no confirm dialog).
- Resets count to 0 and clears localStorage.

## Out of scope (YAGNI)
- Multiple users / cloud sync.
- History / graphs / timestamps.
- Undo (tapping is cheap — if you over-tap, it's funnier).
- Sound effects.

## Technical notes

- **Single file:** everything inline in `index.html`.
- **Keyboard:** spacebar also increments (useful on desktop).
- **Responsive:** number scales with viewport; works on phone and desktop.
- **Mobile:** `<meta name="viewport">` set; prevent double-tap zoom on the tap target; no text selection on taps.
- **Accessibility:** the tap target has an `aria-label`; the number is announced via `aria-live="polite"` so screen readers get updates.

## Deployment

1. Init git repo in `~/Projects/personal/max-o-meter/`.
2. Push to new GitHub repo `max-o-meter` under `maxyouellwork`.
3. Enable GitHub Pages (deploy from `main` branch, root).
4. Share URL with Josh.
