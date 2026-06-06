#!/usr/bin/env python3
"""70s R&B sweetness on the EP-40.

Warm drums, mellow bass, sweet melody lines.
Avoids note 55 (siren supertone).
"""

import rtmidi
import time

# Group A - drums (36-47)
KICK = 36
SNARE = 38
HIHAT = 42
HIHAT_OPEN = 46
RIM = 37
PERC = 40

# Group B - bass (48-59, skip 55)
B_C = 48; B_D = 50; B_Eb = 51; B_E = 52; B_F = 53; B_Ab = 56; B_A = 57; B_Bb = 58

# Group C - melody (60-71) — the sweet spot
C_C = 60; C_D = 62; C_Eb = 63; C_E = 64; C_F = 65; C_G = 67; C_Ab = 68; C_A = 69; C_Bb = 70

# Group D - high twinkle (72-83)
D_C = 72; D_D = 74; D_Eb = 75; D_E = 76; D_F = 77; D_G = 79

BPM = 72  # slow 70s groove
STEPS = 16
step_duration = 60.0 / BPM / 4
NOTE_LEN = 0.03

# 70s R&B pocket — soft kick, brushy hat, snare on 2 and 4
drums = {
    KICK:       [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    SNARE:      [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    HIHAT:      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
    HIHAT_OPEN: [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,0],
}

# Soft velocity — no hard hits, everything pillowy
drum_vel = [65,35,40,35, 80,35,45,40, 60,35,40,35, 80,35,45,35]

# Eb major / Cm — classic 70s soul key
# Progression: Cm7 - Fm7 - Bbmaj7 - Ebmaj7 (vi - ii - V - I)
bass_bars = [
    # Cm7
    [(B_C, 95), None, None, None,
     None, None, None, (B_Eb, 75),
     None, None, None, None,
     (B_C, 80), None, None, None],
    # Fm7
    [(B_F, 95), None, None, None,
     None, None, None, None,
     (B_Ab, 80), None, None, None,
     None, None, (B_F, 75), None],
    # Bbmaj7
    [(B_Bb, 95), None, None, None,
     None, None, None, None,
     None, None, (B_A, 75), None,
     (B_Bb, 80), None, None, None],
    # Ebmaj7
    [(B_Eb, 95), None, None, None,
     None, None, (B_F, 70), None,
     (B_Eb, 80), None, None, None,
     None, None, None, None],
]

# Sweet melody — singable, held notes, Motown feel
melody_bars = [
    # Over Cm7 — longing
    [(C_Eb, 70), None, None, None,
     None, None, None, None,
     (C_G, 75), None, None, None,
     None, None, (C_Eb, 60), None],
    # Over Fm7 — reaching
    [None, None, None, None,
     (C_Ab, 70), None, None, None,
     None, None, (C_G, 65), None,
     (C_F, 60), None, None, None],
    # Over Bbmaj7 — lifting
    [(C_Bb, 75), None, None, None,
     None, None, None, None,
     (C_A, 70), None, None, None,
     None, None, (C_Bb, 65), None],
    # Over Ebmaj7 — resolve sweetly
    [None, None, (C_G, 70), None,
     None, None, None, None,
     (C_Eb, 65), None, None, None,
     None, None, None, None],
]

# High twinkle — barely there, like Rhodes electric piano
high_bars = [
    [None, None, None, None,
     None, None, None, None,
     None, None, None, None,
     None, None, None, (D_Eb, 40)],
    [None, None, None, None,
     None, None, None, None,
     None, None, None, None,
     None, None, None, None],
    [None, None, None, None,
     None, None, None, None,
     None, None, None, (D_F, 40),
     None, None, None, None],
    [None, None, None, None,
     None, None, None, None,
     None, None, None, None,
     (D_Eb, 35), None, None, None],
]

midiout = rtmidi.MidiOut()
midiout.open_port(1)

print(f"70s R&B — {BPM} BPM — Cm7 / Fm7 / Bbmaj7 / Ebmaj7 — Ctrl+C to stop")

bar = 0
try:
    while True:
        chord_idx = bar % 4
        bass = bass_bars[chord_idx]
        melody = melody_bars[chord_idx]
        high = high_bars[chord_idx]

        prev_bass = None
        prev_melody = None
        prev_high = None

        for step in range(STEPS):
            now_notes = []

            bass_hit = bass[step]
            if bass_hit and prev_bass:
                midiout.send_message([0x80, prev_bass, 0])
                prev_bass = None

            melody_hit = melody[step]
            if melody_hit and prev_melody:
                midiout.send_message([0x80, prev_melody, 0])
                prev_melody = None

            high_hit = high[step]
            if high_hit and prev_high:
                midiout.send_message([0x80, prev_high, 0])
                prev_high = None

            v = drum_vel[step]
            for note, hits in drums.items():
                if hits[step]:
                    midiout.send_message([0x90, note, v])
                    now_notes.append(note)

            if bass_hit:
                note, vel = bass_hit
                midiout.send_message([0x90, note, vel])
                prev_bass = note

            if melody_hit:
                note, vel = melody_hit
                midiout.send_message([0x90, note, vel])
                prev_melody = note

            if high_hit:
                note, vel = high_hit
                midiout.send_message([0x90, note, vel])
                prev_high = note

            time.sleep(NOTE_LEN)
            for note in now_notes:
                midiout.send_message([0x80, note, 0])
            time.sleep(step_duration - NOTE_LEN)

        for prev in [prev_bass, prev_melody, prev_high]:
            if prev:
                midiout.send_message([0x80, prev, 0])

        bar += 1
        chords = ["Cm7", "Fm7", "Bbmaj7", "Ebmaj7"]
        if bar % 4 == 0:
            print(f"  progression {bar // 4}...")

except KeyboardInterrupt:
    print("\nStopped")
    for n in range(0, 128):
        midiout.send_message([0x80, n, 0])

midiout.close_port()
print("Done")
