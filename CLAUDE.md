# Riddim

MIDI control scripts for the Teenage Engineering EP-40 Riddim.

## Setup

- Python 3.13 venv at `.venv/`
- Dependencies: `mido`, `python-rtmidi`
- EP-40 connects via USB-C, appears as `"EP-40"` on MIDI port index 1

```bash
source .venv/bin/activate
pip install mido python-rtmidi
```

## EP-40 MIDI Reference

### Note Map
| Group | Notes | Range | Typical Use |
|-------|-------|-------|-------------|
| A | 36–47 | C2–B2 | Drums/percussion |
| B | 48–59 | C3–B3 | Bass/melodic |
| C | 60–71 | C4–B4 | Stabs/FX |
| D | 72–83 | C5–B5 | Additional sounds |

### Common Drum Notes (Group A)
- 36 = Kick, 37 = Rim, 38 = Snare, 39 = Clap
- 42 = Hi-hat closed, 46 = Hi-hat open

### Config
- Default: receives all MIDI channels, sends on ch 1
- MIDI clock off by default (code 101 = receive, 102 = send)
- Program change off by default (code 141 = enable)

## Scripts

- `beat.py` — Basic beat pattern (configurable BPM/loops)
- `dancehall.py` — Dancehall riddim with bass line, loops indefinitely
- `dubstep.py` — Hardcore dubstep with buildup, breakdown, and drop sections

All scripts use `rtmidi` directly. Ctrl+C to stop looping scripts.

## Resources (saved HTML)

Reference pages saved locally from the web:
- Official TE EP-40 guide
- teenagemanual.com AI assistant & learning guide
- Daddy Long Les YouTube tutorials (25-video series)
- ourtinyapps/riddim-n-ting interactive fan guide (GitHub)
