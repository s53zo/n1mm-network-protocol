#!/usr/bin/env python3
"""Ask the sample virtual station to send one XMIT active/release burst."""

from __future__ import annotations

import argparse
import socket


def main() -> int:
    parser = argparse.ArgumentParser(description="Request one XMIT burst from virtual_station.py")
    parser.add_argument("--macro", default="F1Virtual", help="function key caption to advertise")
    parser.add_argument("--seconds", type=float, default=5.0, help="seconds before XMIT release")
    parser.add_argument("--control-ip", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=12071)
    args = parser.parse_args()

    command = f"XMIT {args.seconds:g} {args.macro}".encode("utf-8")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(command, (args.control_ip, args.control_port))

    print(f"requested XMIT {args.seconds:g}s macro={args.macro!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
