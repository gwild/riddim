#!/usr/bin/env python3
"""120 BPM riddim piece designed to lock with the ChucK jam."""

import time

from midi_port import open_midi_out

# ChucK jam default: 120 BPM, 480 PPQ, 8-bar transport.
BPM = 120
STEPS = 16
BARS = 8
STEP_DUR = 60.0 / BPM / 4
DRUM_LEN = 0.035
BASS_LEN = 0.12
STAB_LEN = 0.08

# Group A - drums
KICK = 36
RIM = 37
SNARE = 38
CLAP = 39
PERC = 40
HAT = 42
HAT_OPEN = 46

# Group B - bass. Avoid note 55; it may hold a dub-siren supertone.
B_C = 48
B_EB = 51
B_F = 53
B_AB = 56
B_BB = 58

# Group C/D - stabs and response tones
C_C = 60
C_EB = 63
C_F = 65
C_G = 67
C_BB = 70
D_C = 72
D_EB = 75

drum_bars = [
    {
        KICK:     [1,0,0,0, 0,0,1,0, 0,0,1,0, 0,0,0,0],
        SNARE:    [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        CLAP:     [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        HAT:      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        HAT_OPEN: [0,0,0,1, 0,0,0,0, 0,0,0,1, 0,0,0,0],
        RIM:      [0,0,0,0, 0,0,0,0, 0,1,0,0, 0,0,1,0],
    },
    {
        KICK:     [1,0,0,0, 0,0,0,1, 0,0,1,0, 0,0,0,0],
        SNARE:    [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        CLAP:     [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        HAT:      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        HAT_OPEN: [0,0,0,0, 0,0,0,1, 0,0,0,0, 0,0,0,1],
        PERC:     [0,0,0,0, 0,0,0,0, 0,0,0,1, 0,0,0,0],
    },
]

# Eight bars: call/response bass, syncopated for ChucK's 8-bar loop.
bass_bars = [
    [(B_C, 116), None, None, None, None, None, (B_C, 92), None,
     (B_BB, 104), None, None, (B_AB, 86), None, None, (B_F, 96), None],
    [(B_C, 110), None, None, (B_EB, 82), None, None, None, None,
     (B_F, 98), None, None, None, (B_EB, 86), None, None, None],
    [(B_AB, 104), None, None, None, None, None, (B_AB, 82), None,
     (B_BB, 100), None, None, None, (B_C, 108), None, None, None],
    [(B_F, 104), None, None, None, (B_EB, 86), None, None, None,
     (B_C, 112), None, None, None, None, None, (B_BB, 92), None],
]

stab_bars = [
    [(C_EB, 58), None, None, None, None, None, None, None,
     (C_BB, 52), None, None, None, None, None, None, None],
    [None, None, None, None, (C_F, 54), None, None, None,
     None, None, (C_G, 50), None, None, None, None, None],
    [(D_C, 42), None, None, None, None, None, None, None,
     None, None, None, None, (D_EB, 38), None, None, None],
    [None, None, None, None, None, None, (C_C, 48), None,
     None, None, None, None, (C_EB, 52), None, None, None],
]


def note_on(midiout, note, velocity):
    midiout.send_message([0x90, note, velocity])


def note_off(midiout, note):
    midiout.send_message([0x80, note, 0])


def all_notes_off(midiout):
    for note in range(36, 84):
        note_off(midiout, note)


def play_step(midiout, bar, step):
    now_notes = []
    drums = drum_bars[bar % len(drum_bars)]
    bass = bass_bars[bar % len(bass_bars)][step]
    stab = stab_bars[bar % len(stab_bars)][step]

    for note, hits in drums.items():
        if hits[step]:
            velocity = 112 if note in (KICK, SNARE, CLAP) else 82
            note_on(midiout, note, velocity)
            now_notes.append((note, DRUM_LEN))

    if bass:
        note, velocity = bass
        note_on(midiout, note, velocity)
        now_notes.append((note, BASS_LEN))

    if stab:
        note, velocity = stab
        note_on(midiout, note, velocity)
        now_notes.append((note, STAB_LEN))

    # End short hits while preserving the step grid.
    elapsed = 0.0
    for length in sorted({length for _, length in now_notes}):
        wait = length - elapsed
        if wait > 0:
            time.sleep(wait)
            elapsed = length
        for note, note_len in now_notes:
            if note_len == length:
                note_off(midiout, note)

    rest = STEP_DUR - elapsed
    if rest > 0:
        time.sleep(rest)


def main():
    midiout = open_midi_out()
    print(f"CHUCK SYNC RIDDIM - {BPM} BPM - {BARS}-bar loop - Ctrl+C to stop")
    try:
        bar = 0
        while True:
            for step in range(STEPS):
                play_step(midiout, bar, step)
            bar += 1
            if bar % BARS == 0:
                print(f"  loop {bar // BARS}")
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        all_notes_off(midiout)
        midiout.close_port()
        print("Done")


if __name__ == "__main__":
    main()
