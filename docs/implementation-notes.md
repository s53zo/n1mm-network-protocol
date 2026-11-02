# Implementation Notes

## Parser Rules

Use a stream buffer per TCP connection.

1. Append new bytes to the buffer.
2. Search for `DATA__`.
3. Search for the complete terminator `%~__DATA`.
4. Decode the body as UTF-8.
5. Split on `%`.
6. If the first token is two digits, treat it as the station number.
7. The next token is source station.
8. The next token is command.
9. Remaining tokens are command fields.
10. Keep an incomplete frame or a suffix matching the start of `DATA__` as the
    next read's prefix; discard other noise, including all-NUL bytes.

Do not assume one TCP read equals one frame. These are Python helper rules;
see [the protocol notes](protocol.md#stream-parsing) for the inspected native
receiver's more restrictive buffering behavior.

## Field Escaping

N1MM frames are percent-delimited. Do not place raw `%` in fields. Literal `~`
inside data should be replaced with `!` before framing because `~` terminates a
message body.

## Minimal Virtual Station Behavior

For a useful test station:

- send UDP discovery beacons
- listen for UDP discovery beacons from other stations
- connect to stations heard through discovery (the sample honors advertised IP
  and port; the inspected N1MM receiver uses the UDP source IP and default port)
- listen on TCP `12070`
- optionally connect out to known peer IPs
- send `ECHOREQ`, `CONTESTNAME`, and `STATUS` on new outbound links
- respond to `ECHOREQ` with `ECHO`
- respond to `IAM` with `STOPIAM`
- respond to frequency requests with neutral `CQFREQ`, `FREQ`, and `PASSFREQ`
- keep reading even if no application response is needed

The included `examples/python/virtual_station.py` implements that subset.
`--advertise-ip` selects a local interface for both discovery beacons and
outbound TCP connections, keeping their source IPs consistent with N1MM's
station-address check.

Replies use the outbound connection to the same peer; if it is not open yet,
the sample queues those replies until the connector opens it. It does not send
DATA frames on an accepted inbound connection. `--no-connect-out` therefore
prevents normal request replies. Partial nonblocking writes are buffered and
serialized. Shutdown sends `DISCONNECT_ME` before closing, on a best-effort
basis; a blocked socket may still have unsent bytes.

The default hello/status interval is 10 seconds, inside N1MM's observed
20-second working-state window. `--passive` suppresses these bursts, but retains
discovery, request replies, outbound connections and local control. It is not a
receive-only monitor. The sample does not implement log synchronization and
answers `WHOAREU` with its own empty-log `LASTQAT` sentinel, never the master's
last-QSO timestamp.

To mimic a master station, configure the same identity values that real peers
check in `CONTESTNAME`, `MASTER`, and `STATUS`:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --master \
  --version 1.0.11469.0 \
  --contest CQWPXCW \
  --country-file-version CN \
  --operator-category MULTI-OP \
  --transmitter-category ONE \
  --pass-freq-x100 1407400 \
  --current-freq-x100 1407400 \
  --running
```

Those options produce:

- `CONTESTNAME%N1MMVIRT%CQWPXCW%%`
- `MASTER%N1MMVIRT%`
- `STATUS%1407400%1407400%-1%...%MULTI-OP%ONE%CN%1.0.11469.0%...`

If a real master is already on the network, prefer learning and copying its
settings without claiming master status:

```sh
python3 examples/python/virtual_station.py --mimic-master
```

Set `--version` to the peer's exact version before joining; mimic mode cannot
guarantee discovery admission with the wrong initial version.

This works when the auto-detected `--advertise-ip` is correct and UDP discovery
reaches the real stations. If either condition is not true, specify the local LAN
IP and/or a manual peer:

```sh
python3 examples/python/virtual_station.py \
  --advertise-ip 192.0.2.50 \
  --peer 192.0.2.10 \
  --mimic-master
```

This mode learns from the station named by the next `MASTER` command, then
copies these values from that station's `CONTESTNAME` and `STATUS` messages:

- N1MM version
- contest name
- contest subtype
- country-file version prefix
- operator category
- transmitter category
- mode
- run/CQ state
- pass/CQ and current frequencies

If the master station name is already known, set it directly:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --operator N0CALL \
  --advertise-ip 192.0.2.50 \
  --peer 192.0.2.10 \
  --mimic-master \
  --mimic-source-station N1MMA
```

## Six-NUL Payloads

Six all-NUL bytes may appear on TCP links:

```python
b"\x00" * 6
```

The previous reference described these bytes as observed traffic, but their
origin was not established by this static review. No six-NUL sender or required
ACK was found in the inspected station send/read paths or library connection
checks. This is a bounded negative result, not a whole-program absence claim.
The Python parser discards these bytes outside frames. The sample retains
`--six-nul-response` as an experimental opt-in; it is not a verified protocol
requirement and may interfere with N1MM's restrictive receive buffering.

## QSO-Writing Commands

These commands can modify logs:

- `QSO`
- `REEDITQSO`
- `RESYNCQSO`
- `QSODELETE`
- `DELETEQS`
- `CHECKSUM`
- `CONFIRMED`

Use them only in controlled tests unless your tool is intentionally
participating in log synchronization.

## Version and Contest Matching

The inspected N1MM discovery receiver requires exactly matching version strings;
log-writing paths also gate on version and contest context (see
[command gates](commands.md)). A useful
virtual station should expose configurable `--version` and `--contest` values
and should not claim more compatibility than has been tested.

## Recommended Implementation Order

1. Implement discovery build/parse.
2. Implement DATA frame build/parse with TCP stream buffering.
3. Implement `ECHOREQ`/`ECHO`.
4. Implement `CONTESTNAME` and `STATUS`.
5. Add passive logging for all known commands.
6. Add explicit responses only where your tool needs active behavior.
7. Add QSO-writing commands last, with tests and safeguards.

## Static verification

See [evidence and coverage](evidence.md) for the two inspected versions, method
anchors, unresolved interfaces, and the distinction between native behavior and
sample policy. No live station or contest log was used for validation.
