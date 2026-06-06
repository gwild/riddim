# Riddim

MIDI control scripts for the Teenage Engineering EP-40 Riddim.

## Setup

- Python 3 venv at `.venv/`
- Dependencies listed in `requirements.txt`
- EP-40 connects via USB-C or DIN MIDI through an interface
- Scripts prefer `EP-40`, `Riddim`, `Teenage`, then `AudioBox 1818 VSL`; set `RIDDIM_MIDI_PORT` to a port index or name fragment to override

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
- `dub.py` — Dub pattern with siren sweeps via pitch bend (assign siren supertone to pad first)
- `stutter_dub.py` — Minimal stutter dub at 66 BPM with bass wobble via pitch bend
- `glitch.py` — Slow experimental glitch at 55 BPM, evolving euclidean rhythms, sparse and alien
- `rnb.py` — 70s R&B at 72 BPM, Cm7/Fm7/Bbmaj7/Ebmaj7 progression with sweet melody and high twinkle
- `chuck_sync.py` — 120 BPM 8-bar riddim designed to lock with the ChucK jam transport
- `chuck_sync_16.py` — 120 BPM 16-bar ChucK-synced riddim with a longer developing form
- `chuck_sync_32_aaba.py` — 120 BPM 32-bar AABA ChucK-synced riddim

### Note 55 Warning
Note 55 (Group B pad 5) may have a dub siren supertone assigned. Scripts avoid this note for bass/melody.

All scripts use `rtmidi` directly. Ctrl+C to stop looping scripts.

## Resources (saved HTML)

Reference pages saved locally from the web:
- Official TE EP-40 guide
- teenagemanual.com AI assistant & learning guide
- Daddy Long Les YouTube tutorials (25-video series)
- ourtinyapps/riddim-n-ting interactive fan guide (GitHub)
