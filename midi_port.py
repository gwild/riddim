"""MIDI output selection for Riddim scripts."""

import os

import rtmidi


PREFERRED_PORT_NAMES = ("EP-40", "Riddim", "Teenage", "AudioBox 1818 VSL")


def _find_port(ports, port_spec):
    port_spec = port_spec.strip()
    if port_spec.isdigit():
        index = int(port_spec)
        if 0 <= index < len(ports):
            return index
        raise RuntimeError(f"RIDDIM_MIDI_PORT={port_spec} is outside available ports: {ports}")

    needle = port_spec.lower()
    for index, name in enumerate(ports):
        if needle in name.lower():
            return index

    raise RuntimeError(f"No MIDI output port matched {port_spec!r}. Available ports: {ports}")


def open_midi_out():
    """Open the best available MIDI output port.

    Set RIDDIM_MIDI_PORT to a port index or name fragment to override selection.
    """
    midiout = rtmidi.MidiOut()
    ports = midiout.get_ports()
    if not ports:
        raise RuntimeError("No MIDI output ports available.")

    override = os.environ.get("RIDDIM_MIDI_PORT")
    if override:
        port_index = _find_port(ports, override)
    else:
        port_index = None
        for preferred in PREFERRED_PORT_NAMES:
            try:
                port_index = _find_port(ports, preferred)
                break
            except RuntimeError:
                pass
        if port_index is None:
            port_index = 0

    midiout.open_port(port_index)
    print(f"MIDI out: {ports[port_index]} (port {port_index})")
    return midiout
