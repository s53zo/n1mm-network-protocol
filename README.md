# N1MM Network Protocol Notes and Python Examples

This repository documents the N1MM Logger+ multi-user network protocol and
provides small Python examples for parsing frames, advertising a virtual station,
and sending simple test state messages.

The focus is practical interoperability:

- UDP discovery on port `12070`
- TCP station links on port `12070`
- `DATA__...%~__DATA` frame parsing and generation
- command field layouts and response behavior
- adjacent N1MM UDP/TCP surfaces such as XML broadcasts, rotor, SDR, WSJT/JTDX,
  MMTTY, and TCP radio paths

**Important:** this is not official N1MM documentation. It is a
developer-oriented reference built from information gathered by studying the
network protocol, with proof-of-concept tools and examples for interoperability
testing.

## Quick Start

Parse one frame:

```sh
python3 examples/python/parse_frame.py 'DATA__00%N1MM-A%ECHOREQ%2026-06-02%12:00:00%~__DATA'
```

Run the tests:

```sh
python3 -m unittest discover -s tests
```

Start a passive monitor/virtual station:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --operator N0CALL \
  --advertise-ip 192.0.2.50 \
  --passive
```

By default the virtual station listens for UDP discovery on port `12070` and
opens outbound TCP links to stations it hears. If the auto-detected
`--advertise-ip` is correct for your LAN, this is enough to join and learn:

```sh
python3 examples/python/virtual_station.py --mimic-master
```

Start an active virtual station that advertises itself and connects to a peer:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --operator N0CALL \
  --advertise-ip 192.0.2.50 \
  --peer 192.0.2.10 \
  --version 1.0.11229.0 \
  --contest CQWPXCW \
  --country-file-version CN
```

`--peer` is still useful when you already know a station IP or when UDP
broadcast discovery is blocked. Heard stations and explicit peers are both used.

Learn the real master station's visible contest/status identity and mimic those
values automatically:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --operator N0CALL \
  --advertise-ip 192.0.2.50 \
  --peer 192.0.2.10 \
  --mimic-master
```

With `--mimic-master`, the virtual station watches for `MASTER`, `CONTESTNAME`,
and `STATUS`. After it learns the master station, it advertises matching:

- N1MM version
- contest name and subtype
- country-file version prefix
- operator category
- transmitter category
- mode, run state, and status frequencies

If you already know the master station name, skip waiting for a `MASTER`
announcement:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --operator N0CALL \
  --advertise-ip 192.0.2.50 \
  --peer 192.0.2.10 \
  --mimic-master \
  --mimic-source-station N1MMA
```

Mimic a master station with explicit contest/status identity:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --operator N0CALL \
  --advertise-ip 192.0.2.50 \
  --peer 192.0.2.10 \
  --master \
  --version 1.0.11229.0 \
  --contest CQWPXCW \
  --contest-subtype "" \
  --country-file-version CN \
  --operator-category MULTI-OP \
  --transmitter-category ONE \
  --mode CW \
  --pass-freq-x100 1407400 \
  --current-freq-x100 1407400 \
  --running
```

Use `--master` only if you intentionally want the virtual station to announce
itself as master. To mimic the master's settings while a real master is present,
use `--mimic-master` without `--master`.

To disable discovery-based peer learning:

```sh
python3 examples/python/virtual_station.py --no-auto-discover --peer 192.0.2.10
```

Ask the running virtual station to send an `XMIT` active/release burst:

```sh
python3 examples/python/send_xmit_once.py --seconds 3 --macro F1Virtual
```

Use documentation addresses such as `192.0.2.50` only as examples. Replace them
with addresses from your station LAN.

## Repository Layout

```text
docs/
  protocol.md              Core lifecycle, discovery, framing, liveness, shutdown
  commands.md              All known multi-user TCP commands and field layouts
  ports.md                 Port matrix and options
  payload-examples.md      Copy-paste command/XML/ADIF examples
  implementation-notes.md  Parser and virtual-station guidance
examples/python/
  parse_frame.py           DATA frame parser CLI
  virtual_station.py       Minimal virtual station / protocol monitor
  send_xmit_once.py        Local UDP control helper for virtual_station.py
n1mm_protocol/
  frame.py                 Reusable frame/discovery helpers
  commands.py              Command layout constants
tests/
  test_protocol_frames.py  Unit tests for helpers and examples
```

## Common Use Cases

- Build a log monitor that parses multi-user TCP frames.
- Build a lightweight virtual station for controlled testing.
- Generate known-good `ECHOREQ`, `ECHO`, `STATUS`, `XMIT`, or discovery
  messages.
- Validate whether a received payload is a complete frame or a split TCP
  fragment.
- Inspect adjacent N1MM UDP/XML and WSJT/JTDX integration surfaces.

## Safety Notes

The sample virtual station can send real protocol messages to N1MM instances on
your LAN. Use it first in a test database or non-contest environment.

Important caveats:

- TCP is a byte stream. One `recv()` may contain a partial frame, one frame, or
  multiple frames.
- Six-byte all-NUL TCP payloads have been observed. Their exact role is not
  proven here. Parsers should tolerate and ignore them. The sample virtual
  station only sends them when `--six-nul-response` is enabled.
- `REQCONTESTNAME`, `SKEDSYNC`, and `WHOAREU` are receiver-supported commands,
  but no current sender path is known.
- QSO-writing commands can affect an N1MM log. Do not send `QSO`, `REEDITQSO`,
  `RESYNCQSO`, `QSODELETE`, or checksum repair commands to a live contest log
  unless you intentionally want that behavior.

## Documentation

Start with [docs/protocol.md](docs/protocol.md), then use
[docs/commands.md](docs/commands.md) and
[docs/payload-examples.md](docs/payload-examples.md) while implementing.
