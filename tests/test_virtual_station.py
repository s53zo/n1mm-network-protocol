"""Offline regressions for paired N1MM links and nonblocking writes."""

from __future__ import annotations

import selectors
import unittest
from unittest.mock import Mock, patch

from examples.python.virtual_station import PeerConnection, VirtualStation, parse_args
from n1mm_protocol import parse_frames


class FakeSocket:
    def __init__(self, ip: str, port: int = 12070, sends: list[int | Exception] | None = None):
        self.remote = (ip, port)
        self.sent = b""
        self.sends = list(sends or [])
        self.closed = False

    def getpeername(self):
        return self.remote

    def getsockname(self):
        return ("192.0.2.50", 12070)

    def setsockopt(self, *args):
        pass

    def setblocking(self, value):
        pass

    def send(self, data):
        result = self.sends.pop(0) if self.sends else len(data)
        if isinstance(result, Exception):
            raise result
        self.sent += data[:result]
        return min(result, len(data))

    def close(self):
        self.closed = True


def frames(sock):
    parsed, remainder = parse_frames(sock.sent)
    assert not remainder, remainder
    return parsed


class VirtualStationTests(unittest.TestCase):
    def app(self, *args):
        cfg = parse_args(["--advertise-ip", "192.0.2.50", *args])
        app = VirtualStation(cfg)
        app.selector.close()
        app.selector = Mock()
        return app

    def pair(self, app, ip="192.0.2.10"):
        inbound_sock = FakeSocket(ip, 49152)
        outgoing_sock = FakeSocket(ip)
        inbound = PeerConnection(inbound_sock, "in", False)
        outgoing = PeerConnection(outgoing_sock, "out", True)
        app.connections = {inbound_sock: inbound, outgoing_sock: outgoing}
        return inbound, outgoing

    def test_heartbeat_reply_uses_outgoing_half_of_same_peer(self):
        app = self.app()
        inbound, outgoing = self.pair(app)
        other = FakeSocket("192.0.2.20")
        app.connections[other] = PeerConnection(other, "other", True)
        app.respond_to_frame(inbound, "N1MMA", "ECHOREQ", ("2026-11-02", "12:00:00"))
        self.assertEqual(inbound.sock.sent, b"")
        self.assertEqual(other.sent, b"")
        self.assertEqual(frames(outgoing.sock)[0].tokens,
                         ("N1MMVIRT", "ECHO", "2026-11-02", "12:00:00"))

    def test_reply_waits_for_outgoing_connection(self):
        app = self.app("--passive")
        inbound_sock = FakeSocket("192.0.2.10", 49152)
        inbound = PeerConnection(inbound_sock, "in", False)
        app.connections[inbound_sock] = inbound
        app.respond_to_frame(inbound, "N1MMA", "IAM", (" 0",))
        self.assertEqual(inbound_sock.sent, b"")
        outgoing = FakeSocket("192.0.2.10")
        app.add_connection(outgoing, "out", True)
        self.assertEqual([frame.command for frame in frames(outgoing)], ["STOPIAM"])
        self.assertFalse(app.pending_replies)

    def test_no_unsolicited_hello_on_inbound_connection(self):
        app = self.app()
        inbound = FakeSocket("192.0.2.10", 49152)
        app.add_connection(inbound, "in", False)
        self.assertEqual(inbound.sent, b"")

    def test_connection_is_registered_before_it_is_published(self):
        app = self.app("--passive")
        sock = FakeSocket("192.0.2.10")
        registered = []

        def register(target, events, callback):
            self.assertNotIn(target, app.connections)
            self.assertTrue(app.lock.locked())
            registered.append(target)

        app.selector.register.side_effect = register
        app.add_connection(sock, "out", True)
        self.assertEqual(registered, [sock])
        self.assertIn(sock, app.connections)

    def test_shutdown_during_connection_preparation_prevents_registration(self):
        app = self.app("--passive")
        sock = FakeSocket("192.0.2.10")
        sock.setblocking = lambda value: app.stop_event.set()
        app.add_connection(sock, "out", True)
        self.assertTrue(sock.closed)
        self.assertNotIn(sock, app.connections)
        app.selector.register.assert_not_called()

    def test_registration_failure_closes_socket_without_publishing_it(self):
        for error in (OSError("registration failed"), ValueError("selector closed")):
            with self.subTest(error=error):
                app = self.app("--passive")
                sock = FakeSocket("192.0.2.10")
                app.selector.register.side_effect = error
                app.add_connection(sock, "out", True)
                self.assertTrue(sock.closed)
                self.assertNotIn(sock, app.connections)
                app.selector.modify.assert_not_called()

    def test_broadcast_never_falls_back_to_inbound_writer(self):
        app = self.app()
        inbound = FakeSocket("192.0.2.10", 49152)
        app.connections[inbound] = PeerConnection(inbound, "in", False)
        app.broadcast_to_peer_links(app.frame("XMIT", "0", "", "0", "0", "0"), "release")
        self.assertEqual(inbound.sent, b"")

    def test_whoareu_returns_identity_heartbeat_frequency_empty_log_time(self):
        app = self.app("--passive", "--current-freq-x100", "1407400")
        inbound, outgoing = self.pair(app)
        with patch("examples.python.virtual_station.now_parts", return_value=("2026-11-02", "12:00:00")):
            app.respond_to_frame(inbound, "N1MMA", "WHOAREU", ())
        result = frames(outgoing.sock)
        self.assertEqual([frame.command for frame in result], ["IAM", "ECHOREQ", "FREQ", "LASTQAT"])
        self.assertEqual(result[2].fields, ("1407400",))
        self.assertEqual(result[3].fields, ("1900-01-01 00:00:00",))
        self.assertEqual(inbound.sock.sent, b"")

    def test_contestname_request_repeats_requester_station_in_inner_field(self):
        app = self.app()
        inbound, outgoing = self.pair(app)
        app.respond_to_frame(inbound, "N1MMA", "REQCONTESTNAME", ("ignored", ""))
        response = frames(outgoing.sock)[0]
        self.assertEqual(response.tokens, ("N1MMVIRT", "CONTESTNAME", "N1MMA", "CQWPXCW", ""))

    def test_frequency_requests_broadcast_on_all_outgoing_links(self):
        app = self.app("--pass-freq-x100", "1407400", "--current-freq-x100", "1407500")
        inbound, outgoing = self.pair(app)
        other_sock = FakeSocket("192.0.2.20")
        app.connections[other_sock] = PeerConnection(other_sock, "other", True)
        app.respond_to_frame(inbound, "N1MMA", "REQCQFREQ", ())
        app.respond_to_frame(inbound, "N1MMA", "REQPASSFREQ", ())
        expected = [("CQFREQ", ("1407400",)), ("FREQ", ("1407500",)), ("PASSFREQ", ("1407400",))]
        for sock in (outgoing.sock, other_sock):
            self.assertEqual([(frame.command, frame.fields) for frame in frames(sock)], expected)
        self.assertEqual(inbound.sock.sent, b"")

    def test_defaults_fit_inspected_version_and_liveness_window(self):
        app = self.app()
        self.assertEqual(app.cfg.version, "1.0.11469.0")
        self.assertLess(app.cfg.hello_interval, 20)

    def test_backpressure_preserves_partial_frame_and_following_frame(self):
        app = self.app()
        sock = FakeSocket("192.0.2.10", sends=[7, BlockingIOError(), BlockingIOError()])
        conn = PeerConnection(sock, "out", True)
        app.connections[sock] = conn
        app.send_frame(conn, "IAM", " 0")
        app.send_frame(conn, "FREQ", "1407400")
        self.assertTrue(conn.send_buffer)
        self.assertEqual(app.selector.modify.call_args.args[1], selectors.EVENT_READ | selectors.EVENT_WRITE)
        app.handle_connection_events(sock, selectors.EVENT_WRITE)
        self.assertFalse(conn.send_buffer)
        self.assertEqual([frame.command for frame in frames(sock)], ["IAM", "FREQ"])
        self.assertEqual(app.selector.modify.call_args.args[1], selectors.EVENT_READ)

    def test_disconnect_removes_learned_peer_and_both_links(self):
        app = self.app()
        inbound, outgoing = self.pair(app)
        app.dynamic_peers["192.0.2.10"] = 12070
        app.respond_to_frame(inbound, "N1MMA", "DISCONNECT_ME", ())
        self.assertFalse(app.connections)
        self.assertNotIn("192.0.2.10", app.dynamic_peers)
        self.assertTrue(inbound.sock.closed)
        self.assertTrue(outgoing.sock.closed)

    def test_disconnect_discards_later_frames_from_same_read(self):
        app = self.app("--mimic-master", "--six-nul-response")
        inbound, outgoing = self.pair(app)
        payload = (app.frame("DISCONNECT_ME")
                   + app.frame("ECHOREQ", "2026-11-02", "12:00:00")
                   + app.frame("MASTER", "UNEXPECTED"))
        inbound.sock.recv = lambda size: payload
        app.handle_readable(inbound.sock)
        self.assertFalse(app.connections)
        self.assertFalse(app.pending_replies)
        self.assertIsNone(app.learned_master_station)
        # The opt-in compatibility bytes precede the disconnect only; later
        # messages must not send anything after that terminal command.
        self.assertEqual(inbound.sock.sent, b"\x00" * 6)
        self.assertEqual(outgoing.sock.sent, b"")

    def test_shutdown_announces_disconnect_before_closing(self):
        app = self.app()
        inbound, outgoing = self.pair(app)
        with patch.object(app, "install_signals"), patch("examples.python.virtual_station.threading.Thread"):
            with patch.object(app, "selector_loop", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    app.run()
        self.assertEqual([frame.command for frame in frames(outgoing.sock)], ["DISCONNECT_ME"])
        self.assertTrue(outgoing.sock.closed)
        self.assertTrue(inbound.sock.closed)

    def test_beacon_binds_advertised_local_interface_as_packet_source(self):
        app = self.app()
        sock = Mock()
        sock.sendto.side_effect = lambda *args: app.stop_event.set()
        with patch("examples.python.virtual_station.socket.socket", return_value=sock):
            app.udp_beacon()
        sock.bind.assert_called_once_with(("192.0.2.50", 0))
        self.assertEqual(sock.sendto.call_args.args[1], ("255.255.255.255", 12070))
        sock.close.assert_called_once()

    def test_outgoing_tcp_uses_same_source_interface_as_discovery(self):
        app = self.app("--passive", "--peer", "192.0.2.10")
        sock = FakeSocket("192.0.2.10")

        def connect(*args, **kwargs):
            app.stop_event.set()
            return sock

        with patch("examples.python.virtual_station.socket.create_connection", side_effect=connect) as create:
            app.outgoing_connector()
        create.assert_called_once_with(
            ("192.0.2.10", 12070), timeout=5.0,
            source_address=("192.0.2.50", 0),
        )
        self.assertTrue(sock.closed)

    def test_explicit_advertise_ip_does_not_autodetect(self):
        with patch("examples.python.virtual_station.guess_local_ip", side_effect=AssertionError("network probe")):
            cfg = parse_args(["--advertise-ip", "192.0.2.50"])
        self.assertEqual(cfg.advertise_ip, "192.0.2.50")


if __name__ == "__main__":
    unittest.main()
