# riddim

MIDI control scripts and sample-pack tooling for the [Teenage Engineering EP–40 Riddim](https://teenage.engineering/products/ep-40) — a 128 MB reggae/dub/dancehall sampler and composer.

The EP-40 connects over USB-C (or DIN MIDI through an interface) as a class-compliant MIDI device. These scripts drive it via raw `rtmidi` to play generative patterns, stream its audio out, and curate custom sample packs for loading through the EP Sample Tool.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # mido, python-rtmidi
```

Connect the EP-40 before running any script. `Ctrl+C` stops the looping pattern scripts.

### MIDI port selection

Port discovery lives in `midi_port.py`. Scripts prefer ports matching `EP-40`,
`Riddim`, `Teenage`, then `AudioBox 1818 VSL`. Override with the
`RIDDIM_MIDI_PORT` environment variable (a port index or a name fragment).

## Pattern scripts

Each script sequences a genre over MIDI; BPM and loop counts are configurable in-file.

| Script | Description |
|--------|-------------|
| `beat.py` | Basic configurable beat pattern |
| `dancehall.py` | Dancehall riddim with bass line, loops indefinitely |
| `dubstep.py` | Dubstep with buildup, breakdown, and drop sections |
| `dub.py` | Dub with siren sweeps via pitch bend (assign a siren supertone to a pad first) |
| `dub_95.py` | 95 BPM 32-bar AABA reggae dub — one-drop drums, deep bass, echo repeats |
| `stutter_dub.py` | Minimal stutter dub at 66 BPM with bass wobble |
| `echo_70.py` | 70 BPM dub percussion riddim, one-drop with echo-snare every 4th bar |
| `glitch.py` | Slow experimental glitch at 55 BPM, evolving euclidean rhythms |
| `rnb.py` | 70s R&B at 72 BPM, Cm7/Fm7/Bbmaj7/Ebmaj7 progression |
| `chuck_sync.py` | 120 BPM 8-bar riddim that locks to a ChucK jam transport |
| `chuck_sync_16.py` | 120 BPM 16-bar ChucK-synced riddim |
| `chuck_sync_32_aaba.py` | 120 BPM 32-bar AABA ChucK-synced riddim |
| `rhythm_stream.py` | Stereo Icecast stream from AudioBox 1818VSL inputs 7/8 to `/riddim.mp3` |

## Sample packs — `make_packs.py`

Curates sample packs from local sound libraries and converts them to the EP-40's
native format (**46875 Hz / 16-bit / mono**) for maximum on-device efficiency.

```bash
.venv/bin/python make_packs.py   # writes packs to ep40-packs/
```

Packs produced:

| Pack | Contents |
|------|----------|
| `01_808_kit` | TR-808 one-shots |
| `02_909_kit` | TR-909 one-shots |
| `03_acoustic_drums` | Live-recorded acoustic drums |
| `04_bass_and_synths` | Bass hits and synth stabs |
| `05_funk_breaks` | Full-length funk/soul breaks for chopping |
| `06_break_kit` | Short loopable breaks + an 808 kit to layer over them |

Source paths and pack definitions are configured at the top of `make_packs.py`. Output stays under the EP-40's 999-slot / 128 MB per-set limit.

**Loading onto the device:** connect via USB-C, open the
[EP Sample Tool](https://teenage.engineering/apps/ep-sample-tool) in a WebUSB
browser (Chrome/Edge), and drag in one pack folder at a time.

### Requirements

`make_packs.py` needs `ffmpeg` on `PATH`. If a static binary is present at
`.tools/ffmpeg` it is used in preference (handy when a system ffmpeg is broken).
Both `ep40-packs/` and `.tools/` are gitignored.

## Tempo / loop sync on the EP-40

Imported loops do **not** read embedded tempo metadata. Set a sample's length
in the **TIME** function (BAR or BPM mode), then enable **TIME STRETCH** (Main
mode) so it conforms to the project tempo at constant pitch. Live state uses
"vinyl time" instead (loops repitch when the tempo changes). **Tempo Match**
(hold `SAMPLE` + `TEMPO`) detects incoming line/mic audio and sets the project BPM.

## Streaming

See [`STREAMING.md`](STREAMING.md) for the live stereo route (EP-40 → AudioBox
1818VSL → Icecast `/riddim.mp3`), tmux sessions, verification commands, and the
beelink mix setup.

## EP-40 MIDI reference

### Note map
| Group | Notes | Range | Typical use |
|-------|-------|-------|-------------|
| A | 36–47 | C2–B2 | Drums / percussion |
| B | 48–59 | C3–B3 | Bass / melodic |
| C | 60–71 | C4–B4 | Stabs / FX |
| D | 72–83 | C5–B5 | Additional sounds |

### Common drum notes (Group A)
36 = Kick · 37 = Rim · 38 = Snare · 39 = Clap · 42 = Hi-hat closed · 46 = Hi-hat open

### Config codes
- Receives all MIDI channels, sends on channel 1 by default.
- MIDI clock off by default (101 = receive, 102 = send).
- Program change off by default (141 = enable).

> **Note 55 warning:** Group B pad 5 may have a dub-siren supertone assigned.
> The melodic/bass scripts avoid it. Clear stuck notes between scripts.

## Resources

Reference pages saved locally (`*.html`): the official TE EP-40 guide,
teenagemanual.com AI assistant, the Daddy Long Les YouTube tutorial series, and
the ourtinyapps "riddim-n-ting" fan guide.
