#!/usr/bin/env python3
"""Stream AudioBox 1818VSL inputs 7/8 to Icecast /riddim.mp3 via GStreamer."""

import base64
import http.client
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_ENV = Path("/Users/gregory/milton-locke/.env")
DEFAULT_GST_ROOT = Path("/tmp/gstreamer-osx/runtime")
DEFAULT_PLUGIN_DIR = Path("/tmp/gstreamer-osx/minplugins")
DEFAULT_MOUNT = "/riddim.mp3"
DEFAULT_DEVICE = 84
DEFAULT_LEFT_CHANNEL = 7
DEFAULT_RIGHT_CHANNEL = 8
READ_SIZE = 8192


def load_env(path):
    if not path.exists():
        raise RuntimeError(f"env file not found: {path}")

    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def require(values, key):
    value = values.get(key) or os.environ.get(key)
    if not value:
        raise RuntimeError(f"{key} is required")
    return value


def gst_env(root, plugin_dir):
    env = os.environ.copy()
    env.update(
        {
            "GST_PLUGIN_SYSTEM_PATH_1_0": str(plugin_dir),
            "GST_PLUGIN_PATH_1_0": str(plugin_dir),
            "GST_PLUGIN_SCANNER": str(root / "libexec/gstreamer-1.0/gst-plugin-scanner"),
            "DYLD_FALLBACK_LIBRARY_PATH": str(root / "lib"),
        }
    )
    return env


def select_matrix(input_channels, left_channel, right_channel):
    def row(selected_channel):
        values = ["0.0"] * input_channels
        values[selected_channel - 1] = "1.0"
        return "< " + ", ".join(values) + " >"

    return "< " + ", ".join([row(left_channel), row(right_channel)]) + " >"


def gst_cmd(root, device, left_channel, right_channel):
    input_channels = 18
    matrix = select_matrix(input_channels, left_channel, right_channel)
    return [
        str(root / "bin/gst-launch-1.0"),
        "-q",
        "osxaudiosrc",
        f"device={device}",
        "!",
        f"audio/x-raw,rate=48000,channels={input_channels},layout=interleaved",
        "!",
        "audioconvert",
        "!",
        f"audio/x-raw,format=F32LE,channels={input_channels},rate=48000,layout=interleaved",
        "!",
        "audiomixmatrix",
        f"in-channels={input_channels}",
        "out-channels=2",
        "channel-mask=3",
        f"matrix={matrix}",
        "!",
        "audioconvert",
        "!",
        "audio/x-raw,format=S16LE,layout=interleaved,channels=2,rate=48000",
        "!",
        "lamemp3enc",
        "target=bitrate",
        "bitrate=192",
        "cbr=true",
        "!",
        "fdsink",
        "fd=1",
        "sync=false",
    ]


def send_chunked(conn, chunk):
    conn.send(f"{len(chunk):X}\r\n".encode("ascii"))
    conn.send(chunk)
    conn.send(b"\r\n")


def stream_once(env_path, gst_root, plugin_dir, device, left_channel, right_channel, mount):
    values = load_env(env_path)
    host = require(values, "LAN_ICECAST_HOST")
    port = int(require(values, "ICECAST_PORT"))
    username = require(values, "ICECAST_USERNAME")
    password = require(values, "ICECAST_PASSWORD")
    mount = mount if mount.startswith("/") else f"/{mount}"

    proc = subprocess.Popen(
        gst_cmd(gst_root, device, left_channel, right_channel),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=gst_env(gst_root, plugin_dir),
        bufsize=0,
    )

    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    conn = http.client.HTTPConnection(host, port, timeout=10)
    conn.putrequest("PUT", mount, skip_host=False, skip_accept_encoding=True)
    conn.putheader("Authorization", f"Basic {token}")
    conn.putheader("Content-Type", "audio/mpeg")
    conn.putheader("User-Agent", "Locke-Riddim-GStreamer")
    conn.putheader("Ice-Name", "riddim")
    conn.putheader("Ice-Description", "Locke EP-40 Riddim")
    conn.putheader("Ice-Genre", "riddim")
    conn.putheader("Ice-Public", "0")
    conn.putheader("Transfer-Encoding", "chunked")
    conn.endheaders()

    print(
        f"Streaming AudioBox device {device} channels {left_channel}/{right_channel} "
        f"to http://{host}:{port}{mount}"
    )
    assert proc.stdout is not None
    try:
        while True:
            chunk = proc.stdout.read(READ_SIZE)
            if not chunk:
                stderr = b""
                if proc.stderr is not None:
                    stderr = proc.stderr.read(4096)
                raise RuntimeError(f"GStreamer ended: {stderr.decode(errors='replace')}")
            send_chunked(conn, chunk)
    finally:
        try:
            conn.close()
        finally:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main():
    env_path = Path(os.environ.get("RHYTHM_ENV", DEFAULT_ENV))
    gst_root = Path(os.environ.get("RHYTHM_GST_ROOT", DEFAULT_GST_ROOT))
    plugin_dir = Path(os.environ.get("RHYTHM_GST_PLUGIN_DIR", DEFAULT_PLUGIN_DIR))
    device = int(os.environ.get("RHYTHM_GST_DEVICE", DEFAULT_DEVICE))
    left_channel = int(os.environ.get("RHYTHM_GST_LEFT_CHANNEL", DEFAULT_LEFT_CHANNEL))
    right_channel = int(os.environ.get("RHYTHM_GST_RIGHT_CHANNEL", DEFAULT_RIGHT_CHANNEL))
    mount = os.environ.get("RHYTHM_MOUNT", DEFAULT_MOUNT)

    while True:
        try:
            stream_once(env_path, gst_root, plugin_dir, device, left_channel, right_channel, mount)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(f"stream failed: {exc}", file=sys.stderr)
            time.sleep(2)


if __name__ == "__main__":
    main()
