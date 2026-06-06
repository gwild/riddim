# Riddim Streaming

## Live Route

- EP-40 Riddim analog stereo output feeds AudioBox 1818VSL inputs 7/8.
- `chuck_sync_32_aaba.py` drives the EP-40 at 120 BPM with a 32-bar AABA loop.
- `rhythm_stream.py` captures AudioBox input 7 as left and input 8 as right.
- The stream publishes stereo MP3 to Icecast at `/riddim.mp3`.
- Beelink `gmixer.sh` auto-discovers live Icecast mounts and mixes `/riddim.mp3` with `/jam.mp3` into `/stringdriver-mix`.

## Running Processes

The live Mac sessions are:

```bash
tmux new-session -d -s riddim-piece "cd /Users/gregory/riddim && PYTHONUNBUFFERED=1 /Users/gregory/riddim/.venv/bin/python /Users/gregory/riddim/chuck_sync_32_aaba.py 2>&1 | tee /tmp/riddim/riddim_piece.tmux.log"

tmux new-session -d -s riddim-stream "cd /Users/gregory/riddim && set -a && . /Users/gregory/milton-locke/.env && set +a && PYTHONUNBUFFERED=1 /Users/gregory/riddim/.venv/bin/python /Users/gregory/riddim/rhythm_stream.py 2>&1 | tee /tmp/riddim/riddim_stream.tmux.log"
```

## Verification

Check Icecast:

```bash
curl -fsS http://192.168.1.84:8080/status-json.xsl | python3 -m json.tool
```

Expected live mounts include:

- `/riddim.mp3`
- `/jam.mp3`
- `/stringdriver-mix`

Capture and decode the riddim stream:

```bash
curl --max-time 8 -fsS http://192.168.1.84:8080/riddim.mp3 -o /tmp/riddim/riddim_probe.mp3 || test -s /tmp/riddim/riddim_probe.mp3
afinfo /tmp/riddim/riddim_probe.mp3
afconvert -f WAVE -d LEI16@48000 /tmp/riddim/riddim_probe.mp3 /tmp/riddim/riddim_probe.wav
```

The stream should decode as 2-channel MP3. A healthy recent level was about -34 dBFS RMS and -16 dBFS peak per channel.

## Notes

- Ableton Live can hold the AudioBox input path. If GStreamer sees silence on 7/8 while Ableton meters show signal, close Ableton and restart `riddim-stream`.
- `rhythm_stream.py` sends raw MP3 bytes to Icecast. Do not use HTTP chunk framing for the source body; players will receive invalid MP3 data.
- The beelink mixer may need a restart if `/riddim.mp3` was invalid when it started.

Restart beelink mixer:

```bash
ssh gregory@192.168.1.84 "cd /home/gregory/Documents/Icecast_Monitor && nohup ./gmixer.sh >/tmp/gmixer_stdout.log 2>/tmp/gmixer_stderr.log &"
```
