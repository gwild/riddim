#!/usr/bin/env python3
"""120 BPM, 32-bar AABA EP-40 riddim designed to lock with ChucK."""

import time

from midi_port import open_midi_out


BPM = 120
STEPS = 16
BARS = 32
TICKS_PER_STEP = 120
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


A_BASS = [
    [(B_C, 116, 0), (B_C, 90, 6), (B_BB, 104, 8), (B_AB, 86, 11), (B_F, 96, 14)],
    [(B_C, 110, 0), (B_EB, 82, 3), (B_F, 98, 8), (B_EB, 86, 12)],
    [(B_AB, 106, 0), (B_AB, 82, 6), (B_BB, 100, 8), (B_C, 108, 12)],
    [(B_F, 104, 0), (B_EB, 86, 4), (B_C, 112, 8), (B_BB, 92, 14)],
    [(B_C, 112, 0), (B_C, 84, 5), (B_EB, 92, 8), (B_F, 96, 11)],
    [(B_AB, 106, 0), (B_BB, 92, 4), (B_C, 112, 8), (B_BB, 88, 12)],
    [(B_F, 104, 0), (B_AB, 86, 3), (B_BB, 102, 8), (B_C, 108, 12)],
    [(B_C, 112, 0), (B_EB, 84, 6), (B_F, 98, 8), (B_AB, 84, 10), (B_BB, 92, 12), (B_C, 108, 14)],
]

A2_BASS = [
    [(B_C, 112, 0), (B_EB, 84, 4), (B_F, 96, 6), (B_AB, 92, 10), (B_F, 88, 14)],
    [(B_C, 110, 0), (B_C, 82, 5), (B_BB, 96, 8), (B_AB, 84, 12)],
    [(B_F, 104, 0), (B_AB, 86, 4), (B_BB, 102, 9), (B_C, 108, 13)],
    [(B_AB, 104, 0), (B_F, 92, 6), (B_EB, 86, 10), (B_C, 112, 14)],
    [(B_C, 116, 0), (B_C, 86, 3), (B_EB, 88, 8), (B_F, 94, 11), (B_AB, 88, 14)],
    [(B_BB, 106, 0), (B_AB, 88, 4), (B_F, 96, 8), (B_EB, 86, 12)],
    [(B_C, 112, 0), (B_F, 90, 6), (B_AB, 98, 8), (B_BB, 96, 11), (B_AB, 84, 13)],
    [(B_F, 104, 0), (B_EB, 86, 2), (B_C, 116, 4), (B_BB, 100, 8), (B_AB, 86, 11), (B_C, 118, 14)],
]

B_BASS = [
    [(B_AB, 110, 0), (B_AB, 84, 5), (B_BB, 98, 8), (B_C, 106, 12)],
    [(B_BB, 108, 0), (B_AB, 86, 4), (B_F, 96, 8), (B_EB, 84, 12)],
    [(B_F, 104, 0), (B_AB, 90, 6), (B_BB, 102, 10), (B_C, 106, 14)],
    [(B_AB, 108, 0), (B_BB, 94, 3), (B_C, 112, 8), (B_BB, 88, 12)],
    [(B_F, 102, 0), (B_F, 82, 6), (B_EB, 90, 8), (B_C, 108, 14)],
    [(B_AB, 104, 0), (B_BB, 94, 4), (B_C, 110, 9), (B_BB, 88, 13)],
    [(B_C, 112, 0), (B_BB, 92, 5), (B_AB, 96, 8), (B_F, 92, 12)],
    [(B_EB, 94, 0), (B_F, 100, 4), (B_AB, 104, 8), (B_BB, 108, 12), (B_C, 116, 15)],
]

A3_BASS = [
    [(B_C, 116, 0), (B_C, 90, 6), (B_BB, 104, 8), (B_AB, 86, 11), (B_F, 96, 14)],
    [(B_C, 112, 0), (B_EB, 84, 3), (B_F, 98, 8), (B_AB, 86, 13)],
    [(B_AB, 106, 0), (B_BB, 96, 4), (B_C, 110, 8), (B_BB, 88, 12)],
    [(B_F, 104, 0), (B_EB, 86, 4), (B_C, 112, 8), (B_F, 92, 14)],
    [(B_C, 116, 0), (B_EB, 88, 3), (B_F, 96, 6), (B_AB, 98, 8), (B_BB, 96, 11), (B_C, 112, 14)],
    [(B_BB, 106, 0), (B_AB, 88, 4), (B_F, 96, 8), (B_EB, 86, 12)],
    [(B_C, 112, 0), (B_F, 90, 6), (B_AB, 98, 8), (B_BB, 96, 11), (B_AB, 84, 13)],
    [(B_F, 104, 0), (B_EB, 86, 2), (B_C, 116, 4), (B_BB, 100, 8), (B_AB, 86, 11), (B_C, 118, 14)],
]

FORM = A_BASS + A2_BASS + B_BASS + A3_BASS

STAB_FORM = [
    [(C_EB, 52, 0), (C_BB, 46, 8)],
    [(C_F, 50, 4), (C_G, 46, 10)],
    [(D_C, 38, 0), (D_EB, 34, 12)],
    [(C_C, 46, 6), (C_EB, 48, 12)],
    [(C_C, 46, 0), (C_EB, 44, 8)],
    [(C_AB, 46, 4), (C_BB, 44, 10)],
    [(C_F, 48, 0), (D_C, 36, 12)],
    [(C_G, 40, 2), (C_AB, 40, 6), (C_BB, 42, 10), (D_C, 38, 14)],
] + [
    [(C_EB, 50, 0), (C_AB, 44, 8)],
    [(C_BB, 44, 2), (C_AB, 42, 6), (C_F, 42, 12)],
    [(C_F, 46, 0), (D_C, 36, 8)],
    [(C_AB, 46, 4), (C_BB, 44, 10)],
    [(D_C, 38, 0), (D_EB, 34, 4), (D_F, 32, 8)],
    [(C_BB, 44, 2), (C_AB, 42, 6), (C_F, 44, 12)],
    [(C_EB, 48, 0), (C_AB, 44, 8), (C_BB, 42, 12)],
    [(D_C, 40, 0), (C_BB, 42, 5), (C_AB, 42, 8), (C_F, 44, 11), (C_C, 48, 14)],
] + [
    [(C_AB, 50, 0), (C_BB, 44, 8)],
    [(C_F, 46, 0), (C_EB, 40, 12)],
    [(C_AB, 48, 4), (D_C, 36, 8)],
    [(C_BB, 44, 2), (C_AB, 42, 6), (C_G, 40, 12)],
    [(C_F, 44, 0), (C_EB, 40, 8)],
    [(C_AB, 46, 4), (C_BB, 44, 10)],
    [(C_C, 46, 0), (C_BB, 42, 8), (C_AB, 42, 12)],
    [(C_F, 44, 4), (C_AB, 46, 8), (C_BB, 48, 12), (D_C, 40, 15)],
] + [
    [(C_EB, 52, 0), (C_BB, 46, 8)],
    [(C_F, 50, 4), (C_AB, 44, 13)],
    [(C_AB, 46, 0), (C_BB, 44, 4), (D_C, 38, 8)],
    [(C_F, 48, 0), (C_EB, 42, 4), (C_C, 48, 8)],
    [(D_C, 40, 0), (D_EB, 34, 4), (D_F, 32, 8)],
    [(C_BB, 44, 2), (C_AB, 42, 6), (C_F, 44, 12)],
    [(C_EB, 50, 0), (C_AB, 46, 8), (C_BB, 44, 12)],
    [(D_C, 42, 0), (C_BB, 44, 5), (C_AB, 44, 8), (C_F, 46, 11), (C_C, 50, 14)],
]


def make_bar(events):
    bar = [None] * STEPS
    for note, velocity, step in events:
        bar[step] = (note, velocity)
    return bar


bass_bars = [make_bar(events) for events in FORM]
stab_bars = [make_bar(events) for events in STAB_FORM]


def note_on(midiout, note, velocity):
    midiout.send_message([0x90, note, velocity])


def note_off(midiout, note):
    midiout.send_message([0x80, note, 0])


def all_notes_off(midiout):
    for note in range(36, 84):
        note_off(midiout, note)


def validate_patterns():
    if len(bass_bars) != BARS or len(stab_bars) != BARS:
        raise RuntimeError("32-bar AABA form is incomplete.")
    for index, bar in enumerate(bass_bars + stab_bars):
        if len(bar) != STEPS:
            raise RuntimeError(f"Bar {index + 1} is not {STEPS} steps.")
    for index, drums in enumerate(drum_bars):
        for hits in drums.values():
            if len(hits) != STEPS:
                raise RuntimeError(f"Drum pattern {index + 1} is not {STEPS} steps.")


def bass_note_events():
    events = []
    for bar_index, bar in enumerate(bass_bars):
        for step, hit in enumerate(bar):
            if hit:
                note, velocity = hit
                start_tick = (bar_index * STEPS + step) * TICKS_PER_STEP
                events.append((note, velocity / 127.0, start_tick, 240))
    return events


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
                velocity = 74
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
    print(f"CHUCK SYNC RIDDIM 32 AABA - {BPM} BPM - {BARS}-bar loop - Ctrl+C to stop")
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
