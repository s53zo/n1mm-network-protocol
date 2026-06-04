"""Frame and discovery helpers for the N1MM Logger+ station network."""

from __future__ import annotations

from dataclasses import dataclass


DATA_PREFIX = b"DATA__"
DATA_SUFFIX = b"%~__DATA"
ALL_NUL_PAYLOAD = b"\x00" * 6


@dataclass(frozen=True)
class Frame:
    station_number: int
    station: str
    command: str
    fields: tuple[str, ...]

    @property
    def tokens(self) -> tuple[str, ...]:
        return (self.station, self.command, *self.fields)


@dataclass(frozen=True)
class Discovery:
    station: str
    ip: str
    tcp_port: int
    version: str
    operator: str
    vpn_name: str = ""


def _clean_field(value: object) -> str:
    text = str(value)
    if "%" in text:
        raise ValueError("N1MM percent-delimited fields cannot contain '%'")
    return text.replace("~", "!")


def build_frame(
    station: str,
    command: str,
    *fields: object,
    station_number: int = 0,
) -> bytes:
    """Build one DATA frame.

    The station number is formatted as two digits. Literal tildes inside fields
    are replaced with exclamation marks because the wire format uses `~` as the
    message terminator.
    """

    if not 0 <= station_number <= 99:
        raise ValueError("station_number must fit in two digits")
    tokens = [f"{station_number:02d}", _clean_field(station), _clean_field(command)]
    tokens.extend(_clean_field(field) for field in fields)
    body = "%".join(tokens).encode("utf-8")
    return DATA_PREFIX + body + DATA_SUFFIX


def parse_frames(buffer: bytes) -> tuple[list[Frame], bytes]:
    """Parse complete DATA frames from a TCP byte buffer.

    The return value is `(frames, remainder)`. Keep `remainder` and prepend it
    to the next TCP read.
    """

    frames: list[Frame] = []
    pos = 0
    while True:
        start = buffer.find(DATA_PREFIX, pos)
        if start < 0:
            return frames, buffer[pos:][-len(DATA_PREFIX) :]

        end = buffer.find(DATA_SUFFIX, start)
        if end < 0:
            return frames, buffer[start:]

        body = buffer[start + len(DATA_PREFIX) : end]
        text = body.decode("utf-8", errors="replace")
        tokens = text.split("%")
        if len(tokens) >= 3 and len(tokens[0]) == 2 and tokens[0].isdigit():
            station_number = int(tokens[0])
            station = tokens[1]
            command = tokens[2].upper()
            fields = tuple(tokens[3:])
            frames.append(Frame(station_number, station, command, fields))

        pos = end + len(DATA_SUFFIX)


def build_discovery(
    station: str,
    ip: str,
    tcp_port: int,
    version: str,
    operator: str,
    vpn_name: str = "",
) -> bytes:
    """Build one UDP discovery advertisement."""

    fields = [station, ip, str(tcp_port), version, operator, vpn_name]
    return ("%".join(_clean_field(field) for field in fields) + "%").encode("utf-8")


def parse_discovery(payload: bytes) -> Discovery:
    """Parse a UDP discovery advertisement."""

    text = payload.decode("utf-8", errors="replace").strip("\x00\r\n")
    parts = text.split("%")
    if len(parts) != 7 or parts[-1] != "":
        raise ValueError("discovery payload must have six fields plus trailing '%'")
    station, ip, tcp_port, version, operator, vpn_name, _tail = parts
    return Discovery(
        station=station,
        ip=ip,
        tcp_port=int(tcp_port),
        version=version,
        operator=operator,
        vpn_name=vpn_name,
    )
