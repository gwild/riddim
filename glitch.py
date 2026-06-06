#!/usr/bin/env python3
"""Slow experimental glitch — sparse, evolving, alien dub."""

import rtmidi
import time
import math
import random

KICK = 36
SNARE = 38
RIM = 37
HIHAT = 42
PERC = 40

MELODIC = [48, 49, 50, 51, 52, 53, 54, 55]
STABS = [60, 61, 62, 63]
HIGH = [72, 73, 74]

BPM = 55
STEPS = 16
step_duration = 60.0 / BPM / 4


def send_pitch_bend(midiout, value, channel=0):
    val = max(-8192, min(8191, value)) + 8192
    midiout.send_message([0xE0 | channel, val & 0x7F, (val >> 7) & 0x7F])


def euclidean(hits, steps):
    pattern = []
    bucket = 0
    for _ in range(steps):
        bucket += hits
        if bucket >= steps:
            bucket -= steps
            pattern.append(1)
        else:
            pattern.append(0)
    return pattern


midiout = rtmidi.MidiOut()
midiout.open_port(1)

print(f"SLOW GLITCH — {BPM} BPM — Ctrl+C to stop")

bar = 0
prev_melody = None

try:
    while True:
        # Slowly shifting euclidean densities
        density = 2 + int(2 * math.sin(bar * 0.2))
        kick_pat = euclidean(density, 16)
        rim_pat = euclidean(3, 16)

        # Every other bar: silence or sound
        sparse = bar % 3 == 2

        for step in range(STEPS):
            now_notes = []

            # Big gaps of nothing
            if sparse and step < 8:
                # Just a lonely pitch bend drift
                if prev_melody:
                    drift = int(2000 * math.sin(bar + step * 0.5))
                    send_pitch_bend(midiout, drift)
                time.sleep(step_duration)
                continue

            # Kick — soft
            if kick_pat[step]:
                v = random.randint(50, 85)
                midiout.send_message([0x90, KICK, v])
                now_notes.append(KICK)

            # Rim — ghostly
            if rim_pat[step] and random.random() < 0.6:
                midiout.send_message([0x90, RIM, random.randint(25, 55)])
                now_notes.append(RIM)

            # Snare — rare
            if step == 8 and random.random() < 0.5:
                midiout.send_message([0x90, SNARE, random.randint(50, 80)])
                now_notes.append(SNARE)

            # Melody — one slow note per bar, bending
            if step == 0 and random.random() < 0.6:
                if prev_melody:
                    midiout.send_message([0x80, prev_melody, 0])
                note = random.choice(MELODIC)
                midiout.send_message([0x90, note, random.randint(40, 80)])
                prev_melody = note
                send_pitch_bend(midiout, 0)

            # Slow bend on held note
            if prev_melody and step % 4 == 0:
                bend = int(1500 * math.sin(bar * 0.7 + step * 0.3))
                send_pitch_bend(midiout, bend)

            # Stab — very rare
            if random.random() < 0.04:
                note = random.choice(STABS)
                midiout.send_message([0x90, note, random.randint(40, 70)])
                now_notes.append(note)

            time.sleep(0.03)
            for note in now_notes:
                midiout.send_message([0x80, note, 0])
            time.sleep(step_duration - 0.03)

        bar += 1
        if bar % 2 == 0:
            print(f"  bar {bar}")

except KeyboardInterrupt:
    print("\nStopped")
    for n in range(0, 128):
        midiout.send_message([0x80, n, 0])
    send_pitch_bend(midiout, 0)

midiout.close_port()
print("Done")
