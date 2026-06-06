#!/usr/bin/env python3
"""Hardcore dubstep pattern with a massive breakdown on the EP-40."""

import rtmidi
import time
import random

# Group A - drums
KICK = 36
SNARE = 38
CLAP = 39
HIHAT = 42
HIHAT_OPEN = 46
RIM = 37

# Group B - bass (dirty sub wobble notes)
BASS_C = 48
BASS_Db = 49
BASS_D = 50
BASS_Eb = 51
BASS_E = 52
BASS_F = 53

# Group C - stabs/fx
STAB1 = 60
STAB2 = 62
FX1 = 64
FX2 = 65

BPM = 140
STEPS = 16
step_duration = 60.0 / BPM / 4

DRUM_VEL = 120
BASS_VEL = 127
STAB_VEL = 110
NOTE_LEN = 0.03

# === MAIN DROP — halftime feel, heavy kick+snare ===
drop_drums = {
    KICK:       [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    SNARE:      [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    CLAP:       [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    HIHAT:      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
    HIHAT_OPEN: [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,0],
}

# Wobble bass — rhythmic sub hits
drop_bass = [
    (BASS_C, 127), None, (BASS_C, 100), None,
    (BASS_Eb, 127), None, None, (BASS_C, 90),
    None, None, (BASS_F, 127), None,
    (BASS_Eb, 110), None, (BASS_D, 100), None,
]

# === BUILDUP — snare roll accelerating ===
def play_buildup(midiout):
    print("  >> BUILDUP")
    # 2 bars of accelerating snare rolls
    intervals = [4, 4, 4, 4, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    step_t = step_duration
    for i, interval in enumerate(intervals):
        vel = min(127, 80 + i * 2)
        midiout.send_message([0x90, SNARE, vel])
        if i % 4 == 0:
            midiout.send_message([0x90, KICK, 110])
        time.sleep(NOTE_LEN)
        midiout.send_message([0x80, SNARE, 0])
        midiout.send_message([0x80, KICK, 0])
        time.sleep(step_t * interval - NOTE_LEN)

    # Final hit — everything at once, then silence
    for n in [KICK, SNARE, CLAP, STAB1, BASS_C]:
        midiout.send_message([0x90, n, 127])
    time.sleep(0.15)
    for n in [KICK, SNARE, CLAP, STAB1, BASS_C]:
        midiout.send_message([0x80, n, 0])
    # Silence before drop
    time.sleep(step_duration * 8)


# === BREAKDOWN — sparse, heavy, chaotic ===
break_drums = {
    KICK:       [1,0,0,0, 0,0,0,0, 0,0,0,0, 1,0,1,0],
    SNARE:      [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    CLAP:       [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,1],
    HIHAT:      [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    RIM:        [0,0,1,0, 0,0,0,0, 0,0,1,0, 0,0,0,0],
}

break_bass = [
    (BASS_C, 127), None, None, None,
    None, None, None, None,
    None, None, None, (BASS_F, 127),
    None, None, (BASS_Eb, 110), None,
]

# Stab hits on the breakdown
break_stabs = [
    None, None, None, None,
    None, None, None, None,
    (STAB1, 120), None, None, None,
    None, None, None, (STAB2, 110),
]


def play_pattern(midiout, drums, bass, stabs=None, bars=4, label=""):
    if label:
        print(f"  >> {label}")
    prev_bass = None
    prev_stab = None
    for b in range(bars):
        for step in range(STEPS):
            now_notes = []

            # Bass note-off before new one
            bass_hit = bass[step] if bass else None
            if bass_hit and prev_bass:
                midiout.send_message([0x80, prev_bass, 0])
                prev_bass = None

            # Stab note-off
            stab_hit = stabs[step] if stabs else None
            if stab_hit and prev_stab:
                midiout.send_message([0x80, prev_stab, 0])
                prev_stab = None

            # Drums
            for note, hits in drums.items():
                if hits[step]:
                    midiout.send_message([0x90, note, DRUM_VEL])
                    now_notes.append(note)

            # Bass
            if bass_hit:
                note, vel = bass_hit
                midiout.send_message([0x90, note, vel])
                prev_bass = note

            # Stabs
            if stab_hit:
                note, vel = stab_hit
                midiout.send_message([0x90, note, vel])
                prev_stab = note

            time.sleep(NOTE_LEN)
            for note in now_notes:
                midiout.send_message([0x80, note, 0])
            time.sleep(step_duration - NOTE_LEN)

    # Cleanup
    if prev_bass:
        midiout.send_message([0x80, prev_bass, 0])
    if prev_stab:
        midiout.send_message([0x80, prev_stab, 0])


midiout = rtmidi.MidiOut()
midiout.open_port(1)

print(f"DUBSTEP — {BPM} BPM — Ctrl+C to stop")

try:
    while True:
        play_pattern(midiout, drop_drums, drop_bass, bars=4, label="DROP")
        play_pattern(midiout, drop_drums, drop_bass, bars=4, label="DROP x2")
        play_buildup(midiout)
        play_pattern(midiout, break_drums, break_bass, break_stabs, bars=4, label="BREAKDOWN")
        play_pattern(midiout, drop_drums, drop_bass, bars=4, label="DROP (back)")

except KeyboardInterrupt:
    print("\nStopped")
    all_notes = list(range(36, 84))
    for n in all_notes:
        midiout.send_message([0x80, n, 0])

midiout.close_port()
print("Done")
