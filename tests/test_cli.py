import io
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from basixenum.cli import main, parse_open_ports_from_nmap, run
from basixenum.report import render_triage_report


class CliTests(unittest.TestCase):
    def test_dry_run_with_target_does_not_prompt_or_write_files(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
            out = Path(tmp) / "out"
            stdout = io.StringIO()
            with patch("builtins.input", side_effect=AssertionError("unexpected prompt")):
                with redirect_stdout(stdout):
                    self.assertEqual(main(["enum", "example.test", "--dry-run", "--out", str(out)]), 0)
            self.assertIn("nmap -sS -sC -sV", stdout.getvalue())
            self.assertFalse(out.exists())

    def test_missing_nmap_returns_clear_error(self):
        stderr = io.StringIO()
        with patch("basixenum.cli.subprocess.run", side_effect=FileNotFoundError):
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                self.assertEqual(run(["nmap"], dry_run=False), 127)
        self.assertIn("Required command not found: nmap", stderr.getvalue())

    def test_scan_writes_report_from_nmap_output(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
            def fake_run(command, dry_run):
                self.assertFalse(dry_run)
                prefix = command[command.index("-oA") + 1]
                Path(prefix + ".nmap").write_text("80/tcp open http Apache httpd\n")
                return 0

            with patch("basixenum.cli.run", side_effect=fake_run), redirect_stdout(io.StringIO()):
                self.assertEqual(main(["enum", "example.test", "--out", tmp]), 0)
            reports = list(Path(tmp).rglob("triage_report.txt"))
            self.assertEqual(len(reports), 1)
            self.assertIn("80/tcp http Apache httpd", reports[0].read_text())

    def test_open_ports_are_read_from_normal_nmap_output(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
            scan = Path(tmp) / "nmap.nmap"
            scan.write_text("PORT STATE SERVICE VERSION\n80/tcp open http Apache httpd\n443/tcp closed https\n")
            self.assertEqual(parse_open_ports_from_nmap(scan)[0]["port"], 80)
            self.assertEqual(len(parse_open_ports_from_nmap(scan)), 1)

    def test_report_lists_observed_service_and_group(self):
        text = render_triage_report(
            target="example.test",
            outdir=Path("out"),
            port_entries=[{"port": 80, "proto": "tcp", "service": "http", "version": "Apache"}],
            scan_time="2026-10-27 12:00:00",
        )
        self.assertIn("80/tcp http Apache", text)
        self.assertIn("WEB", text)
        self.assertNotIn("POSSIBLE VULNERABILITY MATCHES", text)


if __name__ == "__main__":
    unittest.main()

