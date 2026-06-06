#!/usr/bin/env python3
"""Send a basic reggae/dancehall beat pattern to the EP-40 Riddim."""

import time

from midi_port import open_midi_out

# EP-40 MIDI Note Map
# Group A (36-47): pads 0-9, enter, period
# Group B (48-59): pads 0-9, enter, period
# Group C (60-71): pads 0-9, enter, period
# Group D (72-83): pads 0-9, enter, period

# Group A pads (typical drum sounds)
KICK = 36       # A0
SNARE = 38      # A2
HIHAT = 42      # A6
HIHAT_OPEN = 46 # A10 (enter)
PERC = 39       # A3

BPM = 90
STEPS = 16
step_duration = 60.0 / BPM / 4  # 16th note duration

# Pattern: 1 = hit, 0 = rest
# Each list is 16 steps (one bar of 16th notes)
pattern = {
    KICK:        [1,0,0,0, 0,0,0,0, 1,0,1,0, 0,0,0,0],
    SNARE:       [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    HIHAT:       [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
    HIHAT_OPEN:  [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,1],
}

VELOCITY = 100
NOTE_LENGTH = 0.05  # short trigger

midiout = open_midi_out()

loops = 4
print(f"Playing {loops} bars at {BPM} BPM — Ctrl+C to stop")

try:
    for loop in range(loops):
        for step in range(STEPS):
            # Send note-ons for this step
            active = []
            for note, hits in pattern.items():
                if hits[step]:
                    midiout.send_message([0x90, note, VELOCITY])
                    active.append(note)

            # Wait, then send note-offs
            time.sleep(NOTE_LENGTH)
            for note in active:
                midiout.send_message([0x80, note, 0])

            # Wait remaining step time
            time.sleep(step_duration - NOTE_LENGTH)

        print(f"  bar {loop + 1}/{loops}")

except KeyboardInterrupt:
    print("\nStopped")
    # All notes off
    for note in pattern:
        midiout.send_message([0x80, note, 0])

midiout.close_port()
print("Done")
