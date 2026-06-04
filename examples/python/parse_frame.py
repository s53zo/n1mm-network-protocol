#!/usr/bin/env python3
"""Parse N1MM DATA frames from a string, stdin, or bytes shown as hex."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from n1mm_protocol import parse_frames  # noqa: E402


def read_payload(args: argparse.Namespace) -> bytes:
    if args.hex:
        return bytes.fromhex(args.hex)
    if args.text:
        return args.text.encode("utf-8")
    return sys.stdin.buffer.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse N1MM DATA__...__DATA frames")
    parser.add_argument("text", nargs="?", help="frame text to parse")
    parser.add_argument("--hex", help="hex bytes to parse instead of text/stdin")
    args = parser.parse_args()

    frames, remainder = parse_frames(read_payload(args))
    for frame in frames:
        print(f"station_number={frame.station_number:02d}")
        print(f"station={frame.station}")
        print(f"command={frame.command}")
        for index, value in enumerate(frame.fields, start=1):
            print(f"field{index}={value}")
        print()

    if remainder:
        print(f"remainder={remainder!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
