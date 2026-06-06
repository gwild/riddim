#!/usr/bin/env python3
"""Minimal stutter dub with low bass wobble — 66 BPM."""

import time
import math

from midi_port import open_midi_out

# Group A - drums
KICK = 36
SNARE = 38
RIM = 37
HIHAT = 42
HIHAT_OPEN = 46

# Group B - bass
BASS_C = 48
BASS_Db = 49
BASS_Eb = 51

BPM = 66
STEPS = 16
step_duration = 60.0 / BPM / 4

DRUM_VEL = 85
BASS_VEL = 120
NOTE_LEN = 0.03


def send_pitch_bend(midiout, value, channel=0):
    val = max(-8192, min(8191, value)) + 8192
    lsb = val & 0x7F
    msb = (val >> 7) & 0x7F
    midiout.send_message([0xE0 | channel, lsb, msb])


# Minimal one-drop, lots of space
drums_a = {
    KICK:       [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    SNARE:      [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    RIM:        [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,0],
    HIHAT:      [1,0,0,0, 0,0,0,0, 0,0,0,0, 1,0,0,0],
}

# Stutter variation — rimshot doubles, ghost hat
drums_b = {
    KICK:       [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    SNARE:      [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    RIM:        [0,0,0,0, 1,0,1,0, 0,0,0,0, 0,1,0,0],
    HIHAT:      [1,0,0,0, 0,0,0,0, 0,0,1,0, 0,0,0,0],
    HIHAT_OPEN: [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,1],
}

# Stutter fill — rapid snare ghosts
drums_fill = {
    KICK:       [0,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
    SNARE:      [0,0,0,0, 0,0,0,0, 1,0,0,1, 0,1,0,1],
    RIM:        [0,0,1,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    HIHAT:      [1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
}

# Bass: single low note, held long — wobble via pitch bend
bass_root = [
    (BASS_C, 127), None, None, None,
    None, None, None, None,
    None, None, None, None,
    None, None, None, None,
]

bass_move = [
    (BASS_C, 127), None, None, None,
    None, None, None, None,
    (BASS_Eb, 110), None, None, None,
    (BASS_Db, 100), None, None, None,
]

# 4-bar phrase: A, A, B, fill
phrase = [
    (drums_a, bass_root, False),
    (drums_a, bass_root, True),   # wobble on bar 2
    (drums_b, bass_move, False),
    (drums_fill, bass_root, True), # wobble on fill
]


def bass_wobble(midiout, duration, depth=2000, rate=2.5):
    """Slow pitch bend wobble over duration."""
    steps = 40
    step_t = duration / steps
    for i in range(steps):
        bend = int(depth * math.sin(2 * math.pi * rate * i / steps))
        send_pitch_bend(midiout, bend)
        time.sleep(step_t)
    send_pitch_bend(midiout, 0)


midiout = open_midi_out()

print(f"STUTTER DUB — {BPM} BPM — Ctrl+C to stop")

bar = 0
try:
    while True:
        drums, bass, wobble = phrase[bar % len(phrase)]
        prev_bass = None

        for step in range(STEPS):
            now_notes = []

            bass_hit = bass[step]
            if bass_hit and prev_bass:
                midiout.send_message([0x80, prev_bass, 0])
                prev_bass = None

            for note, hits in drums.items():
                if hits[step]:
                    # Ghost notes at lower velocity for stutters
                    v = DRUM_VEL if step in [0, 4, 8, 12] else int(DRUM_VEL * 0.6)
                    midiout.send_message([0x90, note, v])
                    now_notes.append(note)

            if bass_hit:
                note, vel = bass_hit
                midiout.send_message([0x90, note, vel])
                prev_bass = note

            # Wobble the bass pitch on marked bars
            if wobble and step == 4 and prev_bass:
                # Non-blocking: just set a slow bend per step
                bend = int(1500 * math.sin(2 * math.pi * step / STEPS))
                send_pitch_bend(midiout, bend)

            if wobble and prev_bass:
                bend = int(1200 * math.sin(2 * math.pi * 1.5 * step / STEPS))
                send_pitch_bend(midiout, bend)

            time.sleep(NOTE_LEN)
            for note in now_notes:
                midiout.send_message([0x80, note, 0])
            time.sleep(step_duration - NOTE_LEN)

        # Reset bend at bar end
        send_pitch_bend(midiout, 0)
        if prev_bass:
            midiout.send_message([0x80, prev_bass, 0])

        bar += 1
        if bar % 4 == 0:
            print(f"  phrase {bar // 4}...")

except KeyboardInterrupt:
    print("\nStopped")
    for n in range(36, 84):
        midiout.send_message([0x80, n, 0])
    send_pitch_bend(midiout, 0)

midiout.close_port()
print("Done")
