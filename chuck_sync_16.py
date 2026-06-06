#!/usr/bin/env python3
"""120 BPM, 16-bar EP-40 riddim designed to lock with the ChucK jam."""

import time

from midi_port import open_midi_out


BPM = 120
STEPS = 16
BARS = 16
STEP_DUR = 60.0 / BPM / 4
DRUM_LEN = 0.035
BASS_LEN = 0.13
STAB_LEN = 0.075
SPARK_LEN = 0.055

# Group A - drums
KICK = 36
RIM = 37
SNARE = 38
CLAP = 39
PERC = 40
SHAKER = 41
HAT = 42
HAT_OPEN = 46

# Group B - bass/melodic. Avoid note 55; it may hold a dub-siren supertone.
B_C = 48
B_EB = 51
B_F = 53
B_AB = 56
B_BB = 58

# Group C/D - stabs and answer tones
C_C = 60
C_EB = 63
C_F = 65
C_G = 67
C_AB = 68
C_BB = 70
D_C = 72
D_EB = 75
D_F = 77


def pattern(*steps):
    hits = [0] * STEPS
    for step in steps:
        hits[step] = 1
    return hits


drum_bars = [
    {
        KICK: pattern(0, 6, 10),
        SNARE: pattern(4, 12),
        CLAP: pattern(4, 12),
        HAT: pattern(0, 2, 4, 6, 8, 10, 12, 14),
        HAT_OPEN: pattern(3, 11),
        RIM: pattern(9, 14),
    },
    {
        KICK: pattern(0, 7, 10),
        SNARE: pattern(4, 12),
        CLAP: pattern(4, 12),
        HAT: pattern(0, 2, 4, 6, 8, 10, 12, 14),
        HAT_OPEN: pattern(7, 15),
        PERC: pattern(11),
    },
    {
        KICK: pattern(0, 5, 8, 13),
        SNARE: pattern(4, 12),
        HAT: pattern(0, 2, 4, 6, 8, 10, 12, 14),
        RIM: pattern(6, 15),
        SHAKER: pattern(1, 5, 9, 13),
    },
    {
        KICK: pattern(0, 6, 10, 15),
        SNARE: pattern(4, 12),
        CLAP: pattern(12),
        HAT: pattern(0, 2, 4, 6, 8, 10, 12, 14),
        HAT_OPEN: pattern(3, 11, 15),
        PERC: pattern(7, 14),
    },
]

# Sixteen-bar form: C center, lift to Ab/Bb, strip down, then answer home.
bass_bars = [
    [(B_C, 116), None, None, None, None, None, (B_C, 90), None,
     (B_BB, 104), None, None, (B_AB, 86), None, None, (B_F, 96), None],
    [(B_C, 110), None, None, (B_EB, 82), None, None, None, None,
     (B_F, 98), None, None, None, (B_EB, 86), None, None, None],
    [(B_AB, 106), None, None, None, None, None, (B_AB, 82), None,
     (B_BB, 100), None, None, None, (B_C, 108), None, None, None],
    [(B_F, 104), None, None, None, (B_EB, 86), None, None, None,
     (B_C, 112), None, None, None, None, None, (B_BB, 92), None],
    [(B_C, 112), None, None, None, None, (B_C, 84), None, None,
     (B_EB, 92), None, None, (B_F, 96), None, None, None, None],
    [(B_AB, 106), None, None, None, (B_BB, 92), None, None, None,
     (B_C, 112), None, None, None, (B_BB, 88), None, None, None],
    [(B_F, 104), None, None, (B_AB, 86), None, None, None, None,
     (B_BB, 102), None, None, None, (B_C, 108), None, None, None],
    [(B_C, 112), None, None, None, None, None, (B_EB, 84), None,
     (B_F, 98), None, (B_AB, 84), None, (B_BB, 92), None, (B_C, 108), None],
    [(B_C, 108), None, None, None, None, None, None, None,
     (B_BB, 96), None, None, None, None, None, (B_AB, 88), None],
    [(B_F, 98), None, None, None, None, None, (B_F, 82), None,
     (B_EB, 90), None, None, None, None, None, None, None],
    [(B_AB, 102), None, None, None, None, None, None, None,
     (B_C, 108), None, None, None, (B_BB, 90), None, None, None],
    [(B_F, 100), None, None, None, (B_EB, 84), None, None, None,
     (B_C, 110), None, None, None, None, None, (B_F, 92), None],
    [(B_C, 116), None, None, (B_EB, 88), None, None, (B_F, 94), None,
     (B_AB, 98), None, None, (B_BB, 96), None, None, (B_C, 112), None],
    [(B_BB, 106), None, None, None, (B_AB, 88), None, None, None,
     (B_F, 96), None, None, None, (B_EB, 86), None, None, None],
    [(B_C, 112), None, None, None, None, None, (B_F, 90), None,
     (B_AB, 98), None, None, (B_BB, 96), None, (B_AB, 84), None, None],
    [(B_F, 104), None, (B_EB, 86), None, (B_C, 116), None, None, None,
     (B_BB, 100), None, None, (B_AB, 86), None, None, (B_C, 118), None],
]

stab_bars = [
    [(C_EB, 54), None, None, None, None, None, None, None,
     (C_BB, 48), None, None, None, None, None, None, None],
    [None, None, None, None, (C_F, 52), None, None, None,
     None, None, (C_G, 48), None, None, None, None, None],
    [(D_C, 40), None, None, None, None, None, None, None,
     None, None, None, None, (D_EB, 36), None, None, None],
    [None, None, None, None, None, None, (C_C, 48), None,
     None, None, None, None, (C_EB, 50), None, None, None],
    [(C_C, 48), None, None, None, None, None, None, None,
     (C_EB, 46), None, None, None, None, None, None, None],
    [None, None, None, None, (C_AB, 48), None, None, None,
     None, None, (C_BB, 46), None, None, None, None, None],
    [(C_F, 50), None, None, None, None, None, None, None,
     None, None, None, None, (D_C, 38), None, None, None],
    [None, None, (C_G, 42), None, None, None, (C_AB, 42), None,
     None, None, (C_BB, 44), None, None, None, (D_C, 40), None],
    [None, None, None, None, None, None, None, None,
     (C_BB, 44), None, None, None, None, None, None, None],
    [(C_F, 44), None, None, None, None, None, None, None,
     None, None, None, None, (C_EB, 42), None, None, None],
    [None, None, None, None, (C_AB, 46), None, None, None,
     (D_C, 38), None, None, None, None, None, None, None],
    [None, None, None, None, None, None, (C_C, 46), None,
     None, None, None, None, (C_F, 44), None, None, None],
    [(D_C, 40), None, None, None, (D_EB, 36), None, None, None,
     (D_F, 34), None, None, None, None, None, None, None],
    [None, None, (C_BB, 44), None, None, None, (C_AB, 42), None,
     None, None, None, None, (C_F, 44), None, None, None],
    [(C_EB, 50), None, None, None, None, None, None, None,
     (C_AB, 46), None, None, None, (C_BB, 44), None, None, None],
    [(D_C, 42), None, None, None, None, (C_BB, 44), None, None,
     (C_AB, 44), None, None, (C_F, 46), None, None, (C_C, 50), None],
]


def note_on(midiout, note, velocity):
    midiout.send_message([0x90, note, velocity])


def note_off(midiout, note):
    midiout.send_message([0x80, note, 0])


def all_notes_off(midiout):
    for note in range(36, 84):
        note_off(midiout, note)


def validate_patterns():
    if len(bass_bars) != BARS or len(stab_bars) != BARS:
        raise RuntimeError("16-bar bass/stab form is incomplete.")
    for index, bar in enumerate(bass_bars + stab_bars):
        if len(bar) != STEPS:
            raise RuntimeError(f"Bar {index + 1} is not {STEPS} steps.")
    for index, drums in enumerate(drum_bars):
        for hits in drums.values():
            if len(hits) != STEPS:
                raise RuntimeError(f"Drum pattern {index + 1} is not {STEPS} steps.")


def play_step(midiout, bar, step):
    now_notes = []
    drums = drum_bars[bar % len(drum_bars)]
    bass = bass_bars[bar % BARS][step]
    stab = stab_bars[bar % BARS][step]

    for note, hits in drums.items():
        if hits[step]:
            if note in (KICK, SNARE, CLAP):
                velocity = 112
            elif note == HAT:
                velocity = 76
            else:
                velocity = 84
            note_on(midiout, note, velocity)
            now_notes.append((note, DRUM_LEN))

    if bass:
        note, velocity = bass
        note_on(midiout, note, velocity)
        now_notes.append((note, BASS_LEN))

    if stab:
        note, velocity = stab
        note_on(midiout, note, velocity)
        length = SPARK_LEN if note >= D_C else STAB_LEN
        now_notes.append((note, length))

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
    validate_patterns()
    midiout = open_midi_out()
    print(f"CHUCK SYNC RIDDIM 16 - {BPM} BPM - {BARS}-bar loop - Ctrl+C to stop")
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
