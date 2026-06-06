#!/usr/bin/env python3
"""Dancehall riddim pattern with bass on the EP-40."""

import rtmidi
import time

# Group A - drums
KICK = 36
SNARE = 38
CLAP = 39
HIHAT = 42
HIHAT_OPEN = 46
RIM = 37

# Group B - bass notes (assuming bass/synth sounds loaded)
BASS_C = 48
BASS_D = 50
BASS_E = 52
BASS_F = 53
BASS_G = 55

BPM = 95
STEPS = 16
step_duration = 60.0 / BPM / 4

# Dancehall: snare on 2 and 4, kick syncopated, busy hats
drums = {
    KICK:       [1,0,0,0, 0,0,1,0, 0,0,1,0, 0,0,0,0],
    SNARE:      [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    CLAP:       [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    HIHAT:      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
    HIHAT_OPEN: [0,0,0,1, 0,0,0,0, 0,0,0,1, 0,0,0,0],
    RIM:        [0,0,0,0, 0,0,0,0, 0,1,0,0, 0,0,1,0],
}

# Bass pattern - root note rhythm with a simple dancehall bounce
# (note, velocity) or None
bass = [
    (BASS_C, 110), None, None, None,
    None, None, (BASS_C, 90), None,
    (BASS_G, 110), None, None, (BASS_F, 80),
    None, None, (BASS_E, 100), None,
]

DRUM_VEL = 100
DRUM_NOTE_LEN = 0.04
BASS_NOTE_LEN = 0.12

midiout = rtmidi.MidiOut()
midiout.open_port(1)  # EP-40

bar = 0
print(f"Dancehall riddim — looping at {BPM} BPM — Ctrl+C to stop")

try:
    prev_bass = None
    while True:
        for step in range(STEPS):
            now_notes = []

            bass_hit = bass[step]
            if bass_hit and prev_bass:
                midiout.send_message([0x80, prev_bass, 0])
                prev_bass = None

            for note, hits in drums.items():
                if hits[step]:
                    midiout.send_message([0x90, note, DRUM_VEL])
                    now_notes.append(note)

            if bass_hit:
                note, vel = bass_hit
                midiout.send_message([0x90, note, vel])
                prev_bass = note

            time.sleep(DRUM_NOTE_LEN)
            for note in now_notes:
                midiout.send_message([0x80, note, 0])

            time.sleep(step_duration - DRUM_NOTE_LEN)

        bar += 1
        if bar % 4 == 0:
            print(f"  {bar} bars...")

except KeyboardInterrupt:
    print("\nStopped")
    for note in list(drums.keys()) + [BASS_C, BASS_D, BASS_E, BASS_F, BASS_G]:
        midiout.send_message([0x80, note, 0])

midiout.close_port()
print("Done")
