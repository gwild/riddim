#!/usr/bin/env python3
"""70 BPM dub percussion for the EP-40 Riddim.

Sparse one-drop, percussion ONLY (no bass/melody) — the dub delay/reverb on
the mix catches the snare. Echo-snare lands every 4th bar for the throw.
Reference: King Tubby / Lee Perry one-drop sparseness. Ctrl+C to stop.
"""
import time

from midi_port import open_midi_out

BPM = 70
STEPS = 16            # 16th-note grid
STEP_DUR = 60.0 / BPM / 4
HIT_LEN = 0.045

# Group A drums
KICK = 36
RIM = 37
SNARE = 38
CLAP = 39
PERC = 40
SHAKER = 41
HAT = 42
HAT_OPEN = 46


def note_on(m, n, v):
    m.send_message([0x90, n, v])


def note_off(m, n):
    m.send_message([0x80, n, 0])


def all_notes_off(m):
    for n in range(36, 48):
        note_off(m, n)


def main():
    m = open_midi_out()
    print(f"ECHO 70 DUB PERCUSSION - {BPM} BPM - one-drop, echo-snare every 4th bar - Ctrl+C to stop")
    bar = 0
    try:
        while True:
            echo_bar = (bar % 4 == 3)        # echo-snare every 4th bar
            for step in range(STEPS):
                hits = []
                # One-drop: kick on beat 3 (step 8), never on the 1.
                if step == 8:
                    hits.append((KICK, 114))
                # Cross-stick / rim backbeat, light.
                if step in (4, 12):
                    hits.append((RIM, 70))
                # Sparse closed hats on the offbeat 8ths.
                if step in (2, 6, 10, 14):
                    hits.append((HAT, 66))
                # Open-hat lift into the next bar.
                if step == 15:
                    hits.append((HAT_OPEN, 82))
                # Shaker texture on the quarter, very light.
                if step in (0, 8):
                    hits.append((SHAKER, 52))
                # Echo-snare: every 4th bar, a strong snare on beat 3 for the
                # delay/reverb throw (the dub "drop").
                if echo_bar and step == 8:
                    hits.append((SNARE, 108))
                for n, v in hits:
                    note_on(m, n, v)
                if hits:
                    time.sleep(HIT_LEN)
                    for n, _ in hits:
                        note_off(m, n)
                    rest = STEP_DUR - HIT_LEN
                else:
                    rest = STEP_DUR
                if rest > 0:
                    time.sleep(rest)
            bar += 1
            if bar % 8 == 0:
                print(f"  loop {bar // 8}")
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        all_notes_off(m)
        m.close_port()
        print("Done")


if __name__ == "__main__":
    main()
