from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from n1mm_protocol import build_discovery, build_frame, parse_discovery, parse_frames
from n1mm_protocol.commands import COMMAND_FIELDS, known_commands
from examples.python.virtual_station import VirtualStation, parse_args


class FrameTests(unittest.TestCase):
    def test_build_frame_uses_n1mm_envelope(self) -> None:
        frame = build_frame("N1MMA", "XMIT", "-1", "F1Virtual", "0", "0", "0")
        self.assertEqual(frame, b"DATA__00%N1MMA%XMIT%-1%F1Virtual%0%0%0%~__DATA")

    def test_parse_concatenated_frames(self) -> None:
        payload = (
            b"noise"
            + build_frame("N1MMA", "ECHOREQ", "2026-06-02", "12:00:00")
            + build_frame("N1MMB", "MASTER", "N1MMB")
        )
        frames, remainder = parse_frames(payload)
        self.assertEqual(remainder, b"")
        self.assertEqual([frame.tokens for frame in frames], [
            ("N1MMA", "ECHOREQ", "2026-06-02", "12:00:00"),
            ("N1MMB", "MASTER", "N1MMB"),
        ])

    def test_parse_split_frame_remainder(self) -> None:
        frame = build_frame("N1MMA", "STATUS", "1407400")
        first, second = frame[:18], frame[18:]
        frames, remainder = parse_frames(first)
        self.assertEqual(frames, [])
        self.assertEqual(remainder, first)
        frames, remainder = parse_frames(remainder + second)
        self.assertEqual(remainder, b"")
        self.assertEqual(frames[0].tokens, ("N1MMA", "STATUS", "1407400"))

    def test_nonzero_station_number(self) -> None:
        frames, remainder = parse_frames(b"DATA__12%N1MMA%FREQ%1407400%~__DATA")
        self.assertEqual(remainder, b"")
        self.assertEqual(frames[0].station_number, 12)
        self.assertEqual(frames[0].tokens, ("N1MMA", "FREQ", "1407400"))

    def test_discovery_roundtrip(self) -> None:
        payload = build_discovery("N1MMA", "192.0.2.10", 12070, "1.0.11229.0", "N0CALL")
        self.assertEqual(payload, b"N1MMA%192.0.2.10%12070%1.0.11229.0%N0CALL%%")
        discovery = parse_discovery(payload)
        self.assertEqual(discovery.station, "N1MMA")
        self.assertEqual(discovery.tcp_port, 12070)
        self.assertEqual(discovery.vpn_name, "")

    def test_command_catalog_has_45_commands(self) -> None:
        self.assertEqual(len(known_commands()), 45)
        self.assertIn("ECHOREQ", COMMAND_FIELDS)
        self.assertIn("WHOAREU", COMMAND_FIELDS)

    def test_payload_examples_cover_known_commands(self) -> None:
        text = (ROOT / "docs" / "payload-examples.md").read_text(encoding="utf-8")
        command_names = {name.upper() for name in re.findall(r"DATA__\d\d%[^%]+%([A-Za-z0-9_]+)%", text)}
        self.assertEqual(set(known_commands()) - command_names, set())

    def test_length_prefixed_log_example_uses_log_command(self) -> None:
        text = (ROOT / "docs" / "payload-examples.md").read_text(encoding="utf-8")
        self.assertIn("<command:3>Log<parameters:64>", text)
        self.assertNotIn("LoggedADIF", text)

    def test_virtual_station_master_identity_options(self) -> None:
        cfg = parse_args([
            "--station",
            "N1MMVIRT",
            "--master",
            "--version",
            "1.0.11229.0",
            "--contest",
            "CQWPXCW",
            "--country-file-version",
            "CN",
            "--pass-freq-x100",
            "1407400",
            "--current-freq-x100",
            "1407400",
            "--running",
        ])
        self.assertTrue(cfg.is_master)
        self.assertEqual(cfg.master_station, "N1MMVIRT")
        self.assertEqual(cfg.version, "1.0.11229.0")
        self.assertEqual(cfg.contest, "CQWPXCW")
        self.assertEqual(cfg.country_file_version, "CN")
        self.assertEqual(cfg.pass_freq_x100, "1407400")
        self.assertEqual(cfg.current_freq_x100, "1407400")
        self.assertEqual(cfg.is_running, "-1")

    def test_virtual_station_learns_master_identity_from_master_and_status(self) -> None:
        cfg = parse_args(["--mimic-master"])
        app = VirtualStation(cfg)

        app.respond_to_frame(None, "N1MMB", "CONTESTNAME", ("N1MMB", "WRONG", ""))  # type: ignore[arg-type]
        self.assertEqual(cfg.contest, "CQWPXCW")

        app.respond_to_frame(None, "N1MMA", "MASTER", ("N1MMA",))  # type: ignore[arg-type]
        app.respond_to_frame(None, "N1MMA", "CONTESTNAME", ("N1MMA", "ARRLDX", "DX"))  # type: ignore[arg-type]
        app.respond_to_frame(
            None,
            "N1MMA",
            "STATUS",
            (
                "1407400",
                "1407500",
                "-1",
                "N0CALL",
                "10",
                "100",
                "CW",
                "MULTI-OP",
                "TWO",
                "ZB",
                "1.0.99999.0",
                "-1",
                "0",
                "0",
                "0",
                "0",
                "0",
            ),
        )  # type: ignore[arg-type]

        self.assertEqual(app.learned_master_station, "N1MMA")
        self.assertEqual(cfg.contest, "ARRLDX")
        self.assertEqual(cfg.contest_subtype, "DX")
        self.assertEqual(cfg.version, "1.0.99999.0")
        self.assertEqual(cfg.country_file_version, "ZB")
        self.assertEqual(cfg.transmitter_category, "TWO")
        self.assertEqual(cfg.pass_freq_x100, "1407400")
        self.assertEqual(cfg.current_freq_x100, "1407500")
        self.assertEqual(cfg.is_running, "-1")

    def test_virtual_station_can_preselect_mimic_source_station(self) -> None:
        cfg = parse_args(["--mimic-master", "--mimic-source-station", "N1MMA"])
        app = VirtualStation(cfg)

        app.respond_to_frame(None, "N1MMA", "CONTESTNAME", ("N1MMA", "CQWWCW", ""))  # type: ignore[arg-type]

        self.assertEqual(app.learned_master_station, "N1MMA")
        self.assertEqual(cfg.contest, "CQWWCW")

    def test_virtual_station_auto_discovers_udp_peers_by_default(self) -> None:
        cfg = parse_args(["--advertise-ip", "192.0.2.50"])
        app = VirtualStation(cfg)

        app.handle_discovery_payload(
            build_discovery("N1MMA", "192.0.2.10", 12070, "1.0.11229.0", "N0CALL"),
            ("192.0.2.10", 12070),
        )

        self.assertTrue(cfg.auto_discover)
        self.assertEqual(app.dynamic_peers["192.0.2.10"], 12070)

    def test_virtual_station_uses_advertised_tcp_port_for_heard_station(self) -> None:
        cfg = parse_args(["--advertise-ip", "192.0.2.50"])
        app = VirtualStation(cfg)

        app.handle_discovery_payload(
            build_discovery("N1MMB", "192.0.2.20", 12123, "1.0.11229.0", "N0CALL"),
            ("192.0.2.20", 12070),
        )

        self.assertEqual(app.dynamic_peers["192.0.2.20"], 12123)

    def test_virtual_station_ignores_own_discovery(self) -> None:
        cfg = parse_args(["--station", "N1MMVIRT", "--advertise-ip", "192.0.2.50"])
        app = VirtualStation(cfg)

        app.handle_discovery_payload(
            build_discovery("N1MMVIRT", "192.0.2.50", 12070, "1.0.11229.0", "N0CALL"),
            ("192.0.2.50", 12070),
        )

        self.assertEqual(app.dynamic_peers, {})


if __name__ == "__main__":
    unittest.main()
