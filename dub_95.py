#!/usr/bin/env python3
"""95 BPM reggae dub instrumental for the EP-40 Riddim.

Sparse 32-bar AABA loop: deep bass, one-drop drums, echo throws, and siren
punctuation. The delay/reverb feel is sequenced as lower-velocity repeats and
long empty space so the EP-40 output can feed external dub processing cleanly.
"""

import time

from midi_port import open_midi_out


BPM = 95
STEPS = 16
BARS = 32
STEP_DUR = 60.0 / BPM / 4

DRUM_LEN = 0.035
HAT_LEN = 0.028
BASS_STEPS = 3
STAB_STEPS = 2
FX_STEPS = 4

# Group A - drums/percussion.
KICK = 36
RIM = 37
SNARE = 38
CLAP = 39
PERC = 40
SHAKER = 41
HAT = 42
HAT_OPEN = 46

# Group B - bass. Avoid note 55; it may hold a dub-siren supertone.
B_C = 48
B_D = 50
B_EB = 51
B_F = 53
B_AB = 56
B_BB = 58

# Group C/D - sparse stabs, siren, and atmospheric answers.
C_C = 60
C_EB = 63
C_F = 65
C_G = 67
C_AB = 68
C_BB = 70
D_C = 72
D_EB = 75
D_F = 77


def hits(*steps):
    pattern = [0] * STEPS
    for step in steps:
        pattern[step] = 1
    return pattern


DRUM_BARS = [
    {
        KICK: hits(8),
        SNARE: hits(8),
        RIM: hits(4, 14),
        HAT: hits(0, 4, 8, 12),
        HAT_OPEN: hits(15),
    },
    {
        KICK: hits(8),
        SNARE: hits(8),
        RIM: hits(6, 14),
        HAT: hits(0, 8, 12),
        SHAKER: hits(3, 11),
    },
    {
        KICK: hits(8, 13),
        SNARE: hits(8),
        RIM: hits(4),
        HAT: hits(0, 4, 8, 12),
        PERC: hits(15),
    },
    {
        KICK: hits(8),
        SNARE: hits(8, 15),
        RIM: hits(4, 11),
        HAT: hits(0, 8),
        HAT_OPEN: hits(7, 15),
    },
]


def bar_events(*events):
    bar = [[] for _ in range(STEPS)]
    for step, note, velocity, length_steps in events:
        bar[step].append((note, velocity, length_steps))
    return bar


A1_BASS = [
    bar_events((0, B_C, 122, 4), (10, B_BB, 92, 2), (14, B_C, 104, 2)),
    bar_events((0, B_C, 116, 3), (8, B_EB, 84, 2), (12, B_F, 94, 2)),
    bar_events((0, B_F, 112, 4), (10, B_EB, 86, 2), (14, B_C, 108, 2)),
    bar_events((0, B_C, 120, 4), (12, B_BB, 94, 2)),
    bar_events((0, B_C, 118, 4), (8, B_C, 78, 2), (14, B_EB, 88, 2)),
    bar_events((0, B_F, 112, 4), (11, B_AB, 84, 2)),
    bar_events((0, B_BB, 108, 3), (8, B_AB, 88, 2), (12, B_F, 96, 2)),
    bar_events((0, B_C, 122, 4), (10, B_BB, 94, 2), (14, B_C, 112, 2)),
]

A2_BASS = [
    bar_events((0, B_C, 120, 4), (10, B_BB, 90, 2)),
    bar_events((0, B_C, 114, 3), (8, B_EB, 82, 2), (12, B_F, 96, 2)),
    bar_events((0, B_AB, 108, 4), (10, B_BB, 92, 2)),
    bar_events((0, B_F, 112, 3), (8, B_EB, 84, 2), (14, B_C, 108, 2)),
    bar_events((0, B_C, 120, 4), (6, B_C, 72, 1), (12, B_EB, 86, 2)),
    bar_events((0, B_F, 112, 4), (10, B_AB, 84, 2), (14, B_F, 90, 2)),
    bar_events((0, B_BB, 108, 4), (8, B_AB, 88, 2), (12, B_F, 94, 2)),
    bar_events((0, B_C, 124, 4), (12, B_BB, 92, 2), (14, B_C, 108, 2)),
]

B_BASS = [
    bar_events((0, B_AB, 112, 4), (10, B_BB, 92, 2)),
    bar_events((0, B_F, 110, 4), (8, B_EB, 84, 2), (12, B_F, 92, 2)),
    bar_events((0, B_D, 102, 3), (8, B_F, 94, 2), (12, B_AB, 86, 2)),
    bar_events((0, B_BB, 110, 4), (12, B_AB, 88, 2)),
    bar_events((0, B_F, 112, 4), (10, B_EB, 84, 2)),
    bar_events((0, B_AB, 108, 4), (8, B_BB, 92, 2), (14, B_C, 104, 2)),
    bar_events((0, B_C, 118, 4), (10, B_BB, 90, 2)),
    bar_events((0, B_F, 112, 3), (8, B_EB, 88, 2), (12, B_C, 114, 2)),
]

A3_BASS = [
    bar_events((0, B_C, 122, 4), (10, B_BB, 92, 2), (14, B_C, 106, 2)),
    bar_events((0, B_C, 116, 3), (8, B_EB, 84, 2), (12, B_F, 94, 2)),
    bar_events((0, B_F, 112, 4), (10, B_EB, 86, 2), (14, B_C, 108, 2)),
    bar_events((0, B_C, 120, 4), (12, B_BB, 94, 2)),
    bar_events((0, B_AB, 108, 4), (8, B_BB, 92, 2), (12, B_C, 108, 2)),
    bar_events((0, B_F, 112, 4), (10, B_EB, 84, 2)),
    bar_events((0, B_C, 118, 3), (8, B_EB, 86, 2), (12, B_F, 96, 2)),
    bar_events((0, B_C, 124, 4), (14, B_C, 112, 2)),
]

BASS_BARS = A1_BASS + A2_BASS + B_BASS + A3_BASS

STAB_BARS = [
    bar_events((4, C_EB, 58, 2), (7, C_EB, 34, 1), (10, C_EB, 24, 1)),
    bar_events(),
    bar_events((12, C_BB, 42, 2), (15, C_BB, 26, 1)),
    bar_events((6, D_C, 36, 3)),
    bar_events((4, C_F, 46, 2), (7, C_F, 30, 1)),
    bar_events(),
    bar_events((14, C_AB, 40, 2)),
    bar_events((0, D_EB, 34, 4), (12, C_C, 44, 2), (15, C_C, 28, 1)),
] + [
    bar_events((4, C_EB, 50, 2), (7, C_EB, 30, 1)),
    bar_events(),
    bar_events((8, C_AB, 42, 2), (11, C_AB, 26, 1)),
    bar_events((14, C_F, 38, 2)),
    bar_events(),
    bar_events((6, D_F, 32, 4)),
    bar_events((12, C_BB, 42, 2), (15, C_BB, 26, 1)),
    bar_events((4, C_EB, 50, 2), (7, C_EB, 30, 1), (10, C_EB, 22, 1)),
] + [
    bar_events((0, C_AB, 48, 2), (3, C_AB, 30, 1)),
    bar_events(),
    bar_events((12, C_F, 42, 2), (15, C_F, 26, 1)),
    bar_events((6, D_C, 34, 4)),
    bar_events((4, C_BB, 42, 2), (7, C_BB, 26, 1)),
    bar_events(),
    bar_events((10, C_AB, 38, 2), (13, C_AB, 24, 1)),
    bar_events((0, D_EB, 34, 4), (14, C_G, 34, 2)),
] + [
    bar_events((4, C_EB, 56, 2), (7, C_EB, 34, 1), (10, C_EB, 24, 1)),
    bar_events(),
    bar_events((12, C_BB, 42, 2), (15, C_BB, 26, 1)),
    bar_events((6, D_C, 36, 3)),
    bar_events((0, D_F, 32, 4), (12, C_AB, 40, 2)),
    bar_events(),
    bar_events((4, C_F, 44, 2), (7, C_F, 28, 1)),
    bar_events((12, C_C, 48, 2), (15, C_C, 30, 1)),
]


def note_on(midiout, note, velocity):
    midiout.send_message([0x90, note, velocity])


def note_off(midiout, note):
    midiout.send_message([0x80, note, 0])


def send_pitch_bend(midiout, value, channel=0):
    value = max(-8192, min(8191, value)) + 8192
    midiout.send_message([0xE0 | channel, value & 0x7F, (value >> 7) & 0x7F])


def all_notes_off(midiout):
    midiout.send_message([0xFC])  # MIDI transport stop, in case the EP-40 sequencer is running.
    for channel in range(16):
        midiout.send_message([0xB0 | channel, 120, 0])  # all sound off
        midiout.send_message([0xB0 | channel, 123, 0])  # all notes off
    for note in range(36, 84):
        note_off(midiout, note)
    send_pitch_bend(midiout, 0)


def validate_patterns():
    if len(BASS_BARS) != BARS or len(STAB_BARS) != BARS:
        raise RuntimeError("32-bar dub form is incomplete.")
    for index, drums in enumerate(DRUM_BARS):
        for note, pattern in drums.items():
            if len(pattern) != STEPS:
                raise RuntimeError(f"Drum pattern {index + 1}, note {note}, is not {STEPS} steps.")


def play_step(midiout, bar, step, active_notes):
    global_step = bar * STEPS + step

    due = [note for note, end_step in active_notes.items() if end_step <= global_step]
    for note in due:
        note_off(midiout, note)
        del active_notes[note]

    now_notes = []
    drums = DRUM_BARS[bar % len(DRUM_BARS)]
    for note, pattern in drums.items():
        if pattern[step]:
            if note in (KICK, SNARE):
                velocity = 106
            elif note == HAT:
                velocity = 56
            elif note == HAT_OPEN:
                velocity = 68
            else:
                velocity = 72
            note_on(midiout, note, velocity)
            now_notes.append((note, HAT_LEN if note in (HAT, HAT_OPEN) else DRUM_LEN))

    for note, velocity, length_steps in BASS_BARS[bar % BARS][step]:
        if note in active_notes:
            note_off(midiout, note)
        note_on(midiout, note, velocity)
        active_notes[note] = global_step + max(length_steps, BASS_STEPS)

    for note, velocity, length_steps in STAB_BARS[bar % BARS][step]:
        note_on(midiout, note, velocity)
        active_notes[note] = global_step + max(length_steps, STAB_STEPS if note < D_C else FX_STEPS)

    # Occasional moving tape/siren bend on atmospheric D notes.
    if bar % 8 in (3, 7) and step in (0, 4, 8, 12):
        send_pitch_bend(midiout, [-1400, 900, -700, 0][step // 4])
    elif step == 0:
        send_pitch_bend(midiout, 0)

    elapsed = 0.0
    for note_len in sorted({length for _, length in now_notes}):
        wait = note_len - elapsed
        if wait > 0:
            time.sleep(wait)
            elapsed = note_len
        for note, length in now_notes:
            if length == note_len:
                note_off(midiout, note)

    rest = STEP_DUR - elapsed
    if rest > 0:
        time.sleep(rest)


def main():
    validate_patterns()
    midiout = open_midi_out()
    all_notes_off(midiout)
    print(f"95 BPM REGGAE DUB - {BARS}-bar AABA - deep bass, sparse drums, echo space")
    try:
        bar = 0
        active_notes = {}
        while True:
            for step in range(STEPS):
                play_step(midiout, bar, step, active_notes)
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
