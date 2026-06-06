#!/usr/bin/env python3
"""Dub pattern with siren on the EP-40 Riddim.

Before running: assign a dub siren supertone to a pad on the EP-40.
Default assumes Group B pad 5 (MIDI note 55). Change SIREN below if different.

The siren sweep uses pitch bend messages to simulate the wail.
"""

import time
import math

from midi_port import open_midi_out

# ---- CONFIG ----
SIREN = 55          # Group B pad 5 — change to match your siren pad
SIREN_GROUP_CH = 0  # MIDI channel 0 = ch 1 (default)

# Group A - drums (one-drop dub style)
KICK = 36
SNARE = 38
RIM = 37
HIHAT = 42
HIHAT_OPEN = 46
PERC = 40

# Group B - bass
BASS_C = 48
BASS_Bb = 58
BASS_G = 55
BASS_F = 53
BASS_Eb = 51

# Use different bass notes to avoid collision with siren
# If siren is on 55 (G), we skip that for bass
BASS_A = 57

BPM = 75  # classic dub tempo
STEPS = 16
step_duration = 60.0 / BPM / 4

DRUM_VEL = 95
BASS_VEL = 110
SIREN_VEL = 100
NOTE_LEN = 0.035

# ---- PATTERNS ----

# One-drop: kick+snare together on beat 3, rimshot accents
dub_drums = {
    KICK:       [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    SNARE:      [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    RIM:        [0,0,0,0, 1,0,0,0, 0,0,0,0, 0,0,1,0],
    HIHAT:      [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
    HIHAT_OPEN: [0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,0,0],
}

# Sparse dub bass — root and fifth, lots of space
dub_bass = [
    (BASS_C, 120), None, None, None,
    None, None, None, None,
    None, None, (BASS_C, 100), None,
    (BASS_A, 110), None, None, None,
]

# Siren schedule: which bars get the siren (0-indexed)
# Siren plays on bars 3, 7, 11, 15... (every 4th bar, offset)
SIREN_EVERY = 4
SIREN_OFFSET = 3


def send_pitch_bend(midiout, value, channel=0):
    """Send pitch bend. value: -8192 to 8191, center = 0."""
    val = max(-8192, min(8191, value)) + 8192
    lsb = val & 0x7F
    msb = (val >> 7) & 0x7F
    midiout.send_message([0xE0 | channel, lsb, msb])


def play_siren_sweep(midiout, duration=2.0, note=SIREN, vel=SIREN_VEL):
    """Play a rising then falling siren wail using pitch bend."""
    steps = 60
    step_t = duration / steps

    # Note on
    send_pitch_bend(midiout, -8192)  # start low
    midiout.send_message([0x90, note, vel])

    # Rise
    for i in range(steps // 2):
        bend = -8192 + int((8191 * 2) * (i / (steps // 2 - 1)))
        send_pitch_bend(midiout, bend)
        time.sleep(step_t)

    # Fall
    for i in range(steps // 2):
        bend = 8191 - int((8191 * 2) * (i / (steps // 2 - 1)))
        send_pitch_bend(midiout, bend)
        time.sleep(step_t)

    # Note off, reset bend
    midiout.send_message([0x80, note, 0])
    send_pitch_bend(midiout, 0)


midiout = open_midi_out()

print(f"DUB — {BPM} BPM — siren on note {SIREN} — Ctrl+C to stop")
print(f"  Assign a dub siren supertone to the pad for note {SIREN} on the EP-40")

bar = 0
try:
    prev_bass = None
    while True:
        # Check if this bar gets a siren
        do_siren = (bar % SIREN_EVERY == SIREN_OFFSET)

        if do_siren:
            # Play siren over this bar (non-blocking would be better,
            # but we play the siren as a solo moment — classic dub style)
            print(f"  bar {bar + 1} — SIREN!")
            play_siren_sweep(midiout, duration=step_duration * STEPS * 0.8)
            # Fill the rest of the bar with silence
            time.sleep(step_duration * STEPS * 0.2)
        else:
            for step in range(STEPS):
                now_notes = []

                bass_hit = dub_bass[step]
                if bass_hit and prev_bass:
                    midiout.send_message([0x80, prev_bass, 0])
                    prev_bass = None

                for note, hits in dub_drums.items():
                    if hits[step]:
                        midiout.send_message([0x90, note, DRUM_VEL])
                        now_notes.append(note)

                if bass_hit:
                    note, vel = bass_hit
                    midiout.send_message([0x90, note, vel])
                    prev_bass = note

                time.sleep(NOTE_LEN)
                for note in now_notes:
                    midiout.send_message([0x80, note, 0])
                time.sleep(step_duration - NOTE_LEN)

            if bar % 4 == 0:
                print(f"  bar {bar + 1}...")

        bar += 1

except KeyboardInterrupt:
    print("\nStopped")
    # All notes off + reset pitch bend
    for n in range(36, 84):
        midiout.send_message([0x80, n, 0])
    send_pitch_bend(midiout, 0)

midiout.close_port()
print("Done")
