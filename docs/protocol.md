# Multi-User Protocol

N1MM Logger+ station networking uses UDP discovery and paired TCP station links.
The default port for both is `12070`.

## UDP Discovery

Stations advertise themselves with UDP text:

```text
<stationName>%<ipAddress>%<tcpPort>%<n1mmVersion>%<operatorCall>%<vpnName>%
```

The trailing percent sign is part of the format. An empty VPN field produces a
payload ending in `operatorCall%%`.

Example:

```text
N1MM-A%192.0.2.10%12070%1.0.11469.0%N0CALL%%
```

In both inspected builds (`1.0.11364.0` and `1.0.11469.0`), the receiver requires
seven split tokens and an **exact** software-version string match. It decodes
these discovery bytes as ASCII even though the sender emits UTF-8; keep station
identifiers ASCII for reliable interoperability.

N1MM's `MultiOpManager.HandleUDPMessage` uses the UDP source IP to create the
station, not the advertised IP. It does not use the advertised TCP port on this
path: the writer defaults to `12070`. The VPN-name field participates in station
replacement when the source address changes. Predefined-station mode suppresses
automatic creation. The Python example instead honors advertised IP/port; that
is sample behavior, not a description of N1MM's discovery receiver.

## TCP Connection Model

N1MM uses paired station links. For two stations `A` and `B`, normal operation
can include both of these connections:

```text
A:<ephemeral> -> B:12070
B:<ephemeral> -> A:12070
```

A reply such as `ECHO` travels on the responder's outbound half, not back along
the requester's writer connection. Each station sends its own `DATA__...__DATA` frames on the TCP connection that
it initiated. A virtual station should be prepared to both accept inbound TCP
and optionally open outbound TCP to known peers.

## DATA Frame Format

Application messages are UTF-8 text frames:

```text
DATA__<stationNrTwoDigits>%<sourceStation>%<command>%<fields...>%~__DATA
```

Examples:

```text
DATA__00%N1MM-A%ECHOREQ%2026-06-02%12:00:00%~__DATA
DATA__00%N1MM-B%ECHO%2026-06-02%12:00:00%~__DATA
DATA__00%N1MM-A%STATUS%1407400%1407400%-1%N0CALL%0%0%CW%MULTI-OP%ONE%CN%1.0.11469.0%-1%0%0%0%0%0%~__DATA
```

The station number is formatted as two digits. Many examples use `00`, but
non-zero two-digit station numbers are accepted by the parser. The source
station is the computer/station name. The command is case-insensitive on
receive.

The initial TCP dispatch uses ASCII decoding; established-reader callbacks use
UTF-8. Non-ASCII startup fields therefore have an additional compatibility risk.

The sender replaces literal `~` inside message data with `!` before framing.
Fields are percent-delimited, so `%` must not be used unescaped inside field
values.

## Stream Parsing

TCP is a byte stream. A parser must handle:

- one frame split across multiple reads
- multiple frames concatenated in one read
- non-frame payloads, including all-NUL bytes
- noise before the next `DATA__` marker

The Python helper uses `%~__DATA` to find complete frames. This is a robust
implementation policy, not an exact copy of N1MM's receiver: its established
reader accumulates text until the buffer starts with `DATA__` and ends with
`__DATA`, removes those markers, then queues messages delimited by `~`.
Noise and partial trailing frames can delay that receiver. Avoid injecting
unframed compatibility bytes into a real link unless independently validated.

## Startup and Link Establishment

A practical startup sequence for a virtual station is:

1. Start a TCP listener on `12070`.
2. Listen for UDP discovery advertisements on `12070`.
3. Add heard stations as outbound TCP peers (the sample uses advertised IP/port;
   N1MM uses the UDP source IP and default port).
4. Send UDP discovery beacons to local broadcast addresses on `12070`.
5. Optionally open outbound TCP links to manually configured peer stations.
6. On a new outbound TCP link, send a small hello/status burst:

```text
DATA__00%N1MMVIRT%ECHOREQ%2026-06-02%12:00:00%~__DATA
DATA__00%N1MMVIRT%CONTESTNAME%N1MMVIRT%CQWPXCW%%~__DATA
DATA__00%N1MMVIRT%STATUS%0%0%0%N0CALL%0%0%CW%MULTI-OP%ONE%CN%1.0.11469.0%-1%0%0%0%0%0%~__DATA
```

If the station should appear as master, include:

```text
DATA__00%N1MMVIRT%MASTER%N1MMVIRT%~__DATA
```

The sample `virtual_station.py` can advertise these identity/status values:

- N1MM version: `--version`
- contest name: `--contest`
- contest subtype: `--contest-subtype`
- country-file version prefix: `--country-file-version`
- operator and transmitter categories: `--operator-category`,
  `--transmitter-category`
- pass/CQ and current radio frequencies multiplied by 100:
  `--pass-freq-x100`, `--current-freq-x100`
- run/CQ state: `--running`
- master state: `--master`, with optional `--master-station`

It can also learn the real master's values with `--mimic-master`. That mode
watches for `MASTER`, then copies the named station's `CONTESTNAME` and `STATUS`
fields into later virtual-station announcements. Use
`--mimic-source-station <station>` when the master station name is already
known.

The sample listens for UDP discovery and connects to heard stations by default.
Use `--no-auto-discover` to disable that behavior and rely only on explicit
`--peer` values.

On its first processed message from a peer, N1MM also sends that peer a
`LASTQAT` before dispatching the command. This can start log synchronization;
the sample is a protocol test station and does not implement that flow.

## Keepalive and Working State

`ECHOREQ` and `ECHO` are the explicit heartbeat pair:

```text
DATA__00%N1MM-A%ECHOREQ%2026-06-02%12:00:00%~__DATA
DATA__00%N1MM-B%ECHO%2026-06-02%12:00:00%~__DATA
```

The `ECHO` response repeats the date and time fields from `ECHOREQ`. N1MM also
refreshes station liveness when other valid messages are processed. A virtual
station should read continuously and respond promptly to heartbeat traffic.
`MultiStation.IsWorking` considers a remote station working only while its
last processed-message timestamp is less than 20 seconds old. This is a status
predicate, not proof of a 20-second socket-close timeout. The example sends
hello/status bursts every 10 seconds by default; its former 30-second default
could leave an idle station temporarily non-working. Native `ECHOREQ` date/time
fields use local date/time; `ECHO` repeats them rather than interpreting them as
UTC. The `TIME` command separately uses UTC.

## Disconnect and Removal

Graceful shutdown uses:

```text
DATA__00%N1MM-A%DISCONNECT_ME%~__DATA
```

After sending `DISCONNECT_ME`, close TCP readers/writers and stop the listener.
On receive, N1MM closes/removes the sending station unless stations are managed
through predefined station settings.

## Responses and Confirmations

There is no general ACK for every `DATA__` message. Responses are command
specific:

| Request/event | Response |
| --- | --- |
| `ECHOREQ` | `ECHO` |
| `IAM` | `STOPIAM` |
| `REQCONTESTNAME` | `CONTESTNAME` |
| `REQCQFREQ` | `CQFREQ` and `FREQ` |
| `REQPASSFREQ` | `PASSFREQ` |
| `CHECKSUM` | `CONFIRMED` when logging at all stations is enabled and contest matches; mismatch can first send repair records |
| `CONFIRMED` | next `CHECKSUM` until checksum window completes |
| `SKEDSYNC` | `SKED` records |
| `WHOAREU` | `IAM`, `ECHOREQ`, `FREQ`, `LASTQAT` |

QSO, status, frequency, talk, packet, and most station-state commands do not
have a true per-message ACK. Some replies are broadcast to all peers, while
others target the requester; see [command response routing](commands.md).

## Evidence and version scope

See [the evidence record](evidence.md) for artifact identities and method anchors.
The newer build serializes `DataArrivalQueing` using a per-instance lock and
explicit buffer field; the older build uses an instance VB static-local buffer
without that lock. Neither finding proves observed runtime behavior.
