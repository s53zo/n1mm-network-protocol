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
N1MM-A%192.0.2.10%12070%1.0.11229.0%N0CALL%%
```

Receivers use the advertisement to learn the station name, address, TCP port,
N1MM version, operator, and optional VPN name. Peers with incompatible N1MM
versions may be rejected by N1MM.

## TCP Connection Model

N1MM uses paired station links. For two stations `A` and `B`, normal operation
can include both of these connections:

```text
A:<ephemeral> -> B:12070
B:<ephemeral> -> A:12070
```

Each station sends its own `DATA__...__DATA` frames on the TCP connection that
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
DATA__00%N1MM-A%STATUS%1407400%1407400%-1%N0CALL%0%0%CW%MULTI-OP%ONE%CN%1.0.11229.0%-1%0%0%0%0%0%~__DATA
```

The station number is formatted as two digits. Many examples use `00`, but
non-zero two-digit station numbers are accepted by the parser. The source
station is the computer/station name. The command is case-insensitive on
receive.

The sender replaces literal `~` inside message data with `!` before framing.
Fields are percent-delimited, so `%` must not be used unescaped inside field
values.

## Stream Parsing

TCP is a byte stream. A parser must handle:

- one frame split across multiple reads
- multiple frames concatenated in one read
- non-frame payloads, including all-NUL bytes
- noise before the next `DATA__` marker

Use the terminator `%~__DATA`, not only `__DATA`, to find complete frames.

## Startup and Link Establishment

A practical startup sequence for a virtual station is:

1. Start a TCP listener on `12070`.
2. Send UDP discovery beacons to local broadcast addresses on `12070`.
3. Optionally open outbound TCP links to known peer stations.
4. On a new TCP link, send a small hello/status burst:

```text
DATA__00%N1MMVIRT%ECHOREQ%2026-06-02%12:00:00%~__DATA
DATA__00%N1MMVIRT%CONTESTNAME%N1MMVIRT%CQWPXCW%%~__DATA
DATA__00%N1MMVIRT%STATUS%0%0%0%N0CALL%0%0%CW%MULTI-OP%ONE%CN%1.0.11229.0%-1%0%0%0%0%0%~__DATA
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

## Keepalive and Working State

`ECHOREQ` and `ECHO` are the explicit heartbeat pair:

```text
DATA__00%N1MM-A%ECHOREQ%2026-06-02%12:00:00%~__DATA
DATA__00%N1MM-B%ECHO%2026-06-02%12:00:00%~__DATA
```

The `ECHO` response repeats the date and time fields from `ECHOREQ`. N1MM also
refreshes station liveness when other valid messages are processed. A virtual
station should read continuously and respond promptly to heartbeat traffic.

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
| `CHECKSUM` | `CONFIRMED` when contest matches |
| `CONFIRMED` | next `CHECKSUM` until checksum window completes |
| `SKEDSYNC` | `SKED` records |
| `WHOAREU` | `IAM`, `ECHOREQ`, `FREQ`, `LASTQAT` |

QSO, status, frequency, talk, packet, and most station-state commands do not
have a true per-message ACK.
