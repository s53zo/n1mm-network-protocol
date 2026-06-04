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
10. Keep any incomplete tail as the next read's prefix.

Do not assume one TCP read equals one frame.

## Field Escaping

N1MM frames are percent-delimited. Do not place raw `%` in fields. Literal `~`
inside data should be replaced with `!` before framing because `~` terminates a
message body.

## Minimal Virtual Station Behavior

For a useful test station:

- send UDP discovery beacons
- listen for UDP discovery beacons from other stations
- connect to stations heard through discovery, using their advertised TCP port
- listen on TCP `12070`
- optionally connect out to known peer IPs
- send `ECHOREQ`, `CONTESTNAME`, and `STATUS` on new links
- respond to `ECHOREQ` with `ECHO`
- respond to `IAM` with `STOPIAM`
- respond to frequency requests with neutral `CQFREQ`, `FREQ`, and `PASSFREQ`
- keep reading even if no application response is needed

The included `examples/python/virtual_station.py` implements that subset.

To mimic a master station, configure the same identity values that real peers
check in `CONTESTNAME`, `MASTER`, and `STATUS`:

```sh
python3 examples/python/virtual_station.py \
  --station N1MMVIRT \
  --master \
  --version 1.0.11229.0 \
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
- `STATUS%1407400%1407400%-1%...%MULTI-OP%ONE%CN%1.0.11229.0%...`

If a real master is already on the network, prefer learning and copying its
settings without claiming master status:

```sh
python3 examples/python/virtual_station.py --mimic-master
```

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

Treat this as an opaque compatibility payload. Parsers should ignore it. The
sample virtual station sends it only when `--six-nul-response` is enabled.

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

N1MM expects peers to use compatible N1MM versions and contest context. A useful
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
