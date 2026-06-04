#!/usr/bin/env python3
"""Minimal N1MM virtual station and protocol monitor.

This example can advertise itself, accept N1MM TCP connections, optionally open
outbound peer links, respond to ECHOREQ with ECHO, send status bursts, and send
test XMIT state changes through a local UDP control port.
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import selectors
import signal
import socket
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from n1mm_protocol import ALL_NUL_PAYLOAD, build_discovery, build_frame, parse_frames  # noqa: E402


def now_parts() -> tuple[str, str]:
    now = dt.datetime.now().astimezone()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")


def guess_local_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def preview(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b <= 126 or b in (10, 13) else "." for b in data)


@dataclass
class Config:
    station: str
    operator: str
    bind_ip: str
    advertise_ip: str
    port: int
    version: str
    contest: str
    contest_subtype: str
    country_file_version: str
    mode: str
    pass_freq_x100: str
    current_freq_x100: str
    is_running: str
    operator_category: str
    transmitter_category: str
    is_master: bool
    master_station: str
    peers: list[str]
    broadcasts: list[str]
    beacon_interval: float
    hello_interval: float
    reconnect_interval: float
    passive: bool
    connect_out: bool
    send_null_response: bool
    control_ip: str
    control_port: int
    log_level: str


@dataclass
class PeerConnection:
    sock: socket.socket
    name: str
    outgoing: bool
    recv_buffer: bytes = b""
    last_hello: float = field(default_factory=lambda: 0.0)


class VirtualStation:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.stop_event = threading.Event()
        self.selector = selectors.DefaultSelector()
        self.connections: dict[socket.socket, PeerConnection] = {}
        self.lock = threading.Lock()

    def frame(self, command: str, *fields: str) -> bytes:
        return build_frame(self.cfg.station, command, *fields)

    def discovery_payload(self) -> bytes:
        return build_discovery(
            self.cfg.station,
            self.cfg.advertise_ip,
            self.cfg.port,
            self.cfg.version,
            self.cfg.operator,
        )

    def install_signals(self) -> None:
        def handler(signum: int, _frame: object) -> None:
            logging.warning("signal %s received, stopping", signum)
            self.stop_event.set()

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def add_connection(self, sock: socket.socket, name: str, outgoing: bool) -> None:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setblocking(False)
        conn = PeerConnection(sock=sock, name=name, outgoing=outgoing)
        with self.lock:
            self.connections[sock] = conn
        self.selector.register(sock, selectors.EVENT_READ, self.handle_readable)
        logging.info("opened tcp[%s] outgoing=%s local=%s remote=%s", name, outgoing, sock.getsockname(), sock.getpeername())
        self.send_hello(conn, "new-connection")

    def close_connection(self, sock: socket.socket) -> None:
        with self.lock:
            conn = self.connections.pop(sock, None)
        try:
            self.selector.unregister(sock)
        except Exception:
            pass
        try:
            sock.close()
        except OSError:
            pass
        if conn:
            logging.warning("closed tcp[%s]", conn.name)

    def send_bytes(self, conn: PeerConnection, payload: bytes, label: str) -> None:
        try:
            conn.sock.sendall(payload)
            logging.info("TX tcp[%s] %s %r", conn.name, label, preview(payload))
        except OSError as exc:
            logging.error("TX tcp[%s] failed: %s", conn.name, exc)
            self.close_connection(conn.sock)

    def send_frame(self, conn: PeerConnection, command: str, *fields: str) -> None:
        self.send_bytes(conn, self.frame(command, *fields), command)

    def send_hello(self, conn: PeerConnection, reason: str) -> None:
        if self.cfg.passive:
            return
        date_s, time_s = now_parts()
        logging.info("sending hello to %s reason=%s", conn.name, reason)
        self.send_frame(conn, "ECHOREQ", date_s, time_s)
        self.send_frame(conn, "CONTESTNAME", self.cfg.station, self.cfg.contest, self.cfg.contest_subtype)
        if self.cfg.is_master:
            self.send_frame(conn, "MASTER", self.cfg.master_station)
        self.send_frame(
            conn,
            "STATUS",
            self.cfg.pass_freq_x100,
            self.cfg.current_freq_x100,
            self.cfg.is_running,
            self.cfg.operator,
            "0",
            "0",
            self.cfg.mode,
            self.cfg.operator_category,
            self.cfg.transmitter_category,
            self.cfg.country_file_version,
            self.cfg.version,
            "-1",
            "0",
            "0",
            "0",
            "0",
            "0",
        )
        conn.last_hello = time.time()

    def send_xmit_burst(self, seconds: float, macro: str) -> None:
        active = self.frame("XMIT", "-1", macro, "0", "0", "0")
        release = self.frame("XMIT", "0", "", "0", "0", "0")
        self.broadcast_to_peer_links(active, "XMIT-active")
        self.stop_event.wait(seconds)
        self.broadcast_to_peer_links(release, "XMIT-release")

    def broadcast_to_peer_links(self, payload: bytes, label: str) -> None:
        with self.lock:
            conns = [conn for conn in self.connections.values() if conn.outgoing]
            if not conns:
                conns = list(self.connections.values())
        for conn in conns:
            self.send_bytes(conn, payload, label)

    def respond_to_frame(self, conn: PeerConnection, station: str, command: str, fields: tuple[str, ...]) -> None:
        logging.info("RX tcp[%s] station=%s command=%s fields=%r", conn.name, station, command, fields)
        if command == "ECHOREQ":
            date_s = fields[0] if len(fields) > 0 else now_parts()[0]
            time_s = fields[1] if len(fields) > 1 else now_parts()[1]
            self.send_frame(conn, "ECHO", date_s, time_s)
        elif command == "IAM":
            self.send_frame(conn, "STOPIAM")
        elif command == "REQCQFREQ":
            self.send_frame(conn, "CQFREQ", self.cfg.pass_freq_x100)
            self.send_frame(conn, "FREQ", self.cfg.current_freq_x100)
        elif command == "REQPASSFREQ":
            self.send_frame(conn, "PASSFREQ", self.cfg.pass_freq_x100)
        elif command == "REQCONTESTNAME":
            self.send_frame(conn, "CONTESTNAME", self.cfg.station, self.cfg.contest, self.cfg.contest_subtype)
        elif command == "WHOAREU":
            self.send_frame(conn, "IAM", " 0")
            self.send_hello(conn, "WHOAREU")

    def handle_readable(self, sock: socket.socket) -> None:
        conn = self.connections.get(sock)
        if not conn:
            return
        try:
            data = sock.recv(65535)
        except OSError as exc:
            logging.error("RX tcp[%s] failed: %s", conn.name, exc)
            self.close_connection(sock)
            return
        if not data:
            self.close_connection(sock)
            return

        logging.debug("RXRAW tcp[%s] %r", conn.name, preview(data))
        if data == b"\x00" * len(data):
            logging.info("RX tcp[%s] all-NUL bytes=%d", conn.name, len(data))

        conn.recv_buffer += data
        frames, conn.recv_buffer = parse_frames(conn.recv_buffer)
        for frame in frames:
            if self.cfg.send_null_response:
                self.send_bytes(conn, ALL_NUL_PAYLOAD, "six-NUL-compat")
            self.respond_to_frame(conn, frame.station, frame.command, frame.fields)

    def tcp_server(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.cfg.bind_ip, self.cfg.port))
        server.listen(20)
        server.settimeout(1.0)
        logging.warning("TCP listening on %s:%d", self.cfg.bind_ip, self.cfg.port)
        try:
            while not self.stop_event.is_set():
                try:
                    client, addr = server.accept()
                except socket.timeout:
                    continue
                self.add_connection(client, f"in:{addr[0]}:{addr[1]}", outgoing=False)
        finally:
            server.close()

    def outgoing_connector(self) -> None:
        if not self.cfg.connect_out:
            return
        while not self.stop_event.is_set():
            with self.lock:
                names = {conn.name for conn in self.connections.values()}
            for peer in self.cfg.peers:
                name = f"out:{peer}:{self.cfg.port}"
                if name in names:
                    continue
                try:
                    sock = socket.create_connection((peer, self.cfg.port), timeout=5.0)
                    self.add_connection(sock, name, outgoing=True)
                except OSError as exc:
                    logging.info("connect %s failed: %s", name, exc)
            self.stop_event.wait(self.cfg.reconnect_interval)

    def udp_beacon(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            while not self.stop_event.is_set():
                payload = self.discovery_payload()
                for host in self.cfg.broadcasts:
                    try:
                        sock.sendto(payload, (host, self.cfg.port))
                        logging.info("TX udp discovery to %s:%d %r", host, self.cfg.port, payload.decode())
                    except OSError as exc:
                        logging.warning("discovery to %s failed: %s", host, exc)
                self.stop_event.wait(self.cfg.beacon_interval)
        finally:
            sock.close()

    def control_listener(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.cfg.control_ip, self.cfg.control_port))
        sock.settimeout(1.0)
        logging.warning("control UDP listening on %s:%d", self.cfg.control_ip, self.cfg.control_port)
        try:
            while not self.stop_event.is_set():
                try:
                    data, _addr = sock.recvfrom(4096)
                except socket.timeout:
                    continue
                text = data.decode("utf-8", errors="replace").strip()
                parts = text.split(maxsplit=2)
                if not parts:
                    continue
                if parts[0].upper() == "XMIT":
                    seconds = float(parts[1]) if len(parts) > 1 else 5.0
                    macro = parts[2] if len(parts) > 2 else "F1Virtual"
                    threading.Thread(target=self.send_xmit_burst, args=(seconds, macro), daemon=True).start()
                elif parts[0].upper() == "STOP":
                    self.stop_event.set()
        finally:
            sock.close()

    def selector_loop(self) -> None:
        while not self.stop_event.is_set():
            for key, _mask in self.selector.select(timeout=1.0):
                key.data(key.fileobj)
            now = time.time()
            for conn in list(self.connections.values()):
                if now - conn.last_hello >= self.cfg.hello_interval:
                    self.send_hello(conn, "periodic")

    def run(self) -> None:
        self.install_signals()
        threads = [
            threading.Thread(target=self.tcp_server, daemon=True),
            threading.Thread(target=self.outgoing_connector, daemon=True),
            threading.Thread(target=self.udp_beacon, daemon=True),
            threading.Thread(target=self.control_listener, daemon=True),
        ]
        for thread in threads:
            thread.start()
        try:
            self.selector_loop()
        finally:
            self.stop_event.set()
            for sock in list(self.connections):
                self.close_connection(sock)


def parse_args(argv: Iterable[str]) -> Config:
    parser = argparse.ArgumentParser(description="Minimal N1MM virtual station / monitor")
    parser.add_argument("--station", default="N1MMVIRT")
    parser.add_argument("--operator", default="N0CALL")
    parser.add_argument("--bind-ip", default="0.0.0.0")
    parser.add_argument("--advertise-ip", default=guess_local_ip())
    parser.add_argument("--port", type=int, default=12070)
    parser.add_argument("--version", default="1.0.11229.0")
    parser.add_argument("--contest", default="CQWPXCW")
    parser.add_argument("--contest-subtype", default="")
    parser.add_argument("--country-file-version", default="CN", help="wl_cty.dat version prefix advertised in STATUS")
    parser.add_argument("--mode", default="CW")
    parser.add_argument("--pass-freq-x100", default="0", help="pass/CQ frequency multiplied by 100")
    parser.add_argument("--current-freq-x100", default="0", help="current radio frequency multiplied by 100")
    parser.add_argument("--running", action="store_true", help="advertise run/CQ state as true")
    parser.add_argument("--operator-category", default="MULTI-OP")
    parser.add_argument("--transmitter-category", default="ONE")
    parser.add_argument("--master", action="store_true", help="send MASTER announcements for this station")
    parser.add_argument("--master-station", help="station name to advertise as master; defaults to --station")
    parser.add_argument("--peer", action="append", default=[], help="peer IP to connect to; repeat for multiple peers")
    parser.add_argument("--broadcast", action="append", default=["255.255.255.255"], help="UDP discovery destination")
    parser.add_argument("--beacon-interval", type=float, default=10.0)
    parser.add_argument("--hello-interval", type=float, default=30.0)
    parser.add_argument("--reconnect-interval", type=float, default=5.0)
    parser.add_argument("--passive", action="store_true", help="monitor only; do not send hello/status bursts")
    parser.add_argument("--no-connect-out", action="store_true", help="do not open outbound TCP peer links")
    parser.add_argument("--six-nul-response", action="store_true", help="send observed six-NUL compatibility bytes after DATA frames")
    parser.add_argument("--control-ip", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=12071)
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args(list(argv))

    return Config(
        station=args.station,
        operator=args.operator,
        bind_ip=args.bind_ip,
        advertise_ip=args.advertise_ip,
        port=args.port,
        version=args.version,
        contest=args.contest,
        contest_subtype=args.contest_subtype,
        country_file_version=args.country_file_version,
        mode=args.mode,
        pass_freq_x100=args.pass_freq_x100,
        current_freq_x100=args.current_freq_x100,
        is_running="-1" if args.running else "0",
        operator_category=args.operator_category,
        transmitter_category=args.transmitter_category,
        is_master=args.master,
        master_station=args.master_station or args.station,
        peers=args.peer,
        broadcasts=args.broadcast,
        beacon_interval=args.beacon_interval,
        hello_interval=args.hello_interval,
        reconnect_interval=args.reconnect_interval,
        passive=args.passive,
        connect_out=not args.no_connect_out,
        send_null_response=args.six_nul_response,
        control_ip=args.control_ip,
        control_port=args.control_port,
        log_level=args.log_level,
    )


def main(argv: Iterable[str]) -> int:
    cfg = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, cfg.log_level),
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.warning("advertising %s at %s:%d", cfg.station, cfg.advertise_ip, cfg.port)
    VirtualStation(cfg).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
