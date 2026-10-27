import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from basixenum.runner import run_task
from basixenum.tasks.base import ReconTask


class RunnerTests(unittest.TestCase):
    def test_missing_optional_command_is_reported(self):
        task = ReconTask(name="missing", category="WEB", command=["missing-tool"])
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
            with patch("basixenum.runner.subprocess.run", side_effect=FileNotFoundError):
                result = run_task(task, Path(tmp))
            self.assertEqual(result.returncode, 127)
            self.assertIn("missing-tool", result.stderr)
            self.assertTrue((Path(tmp) / "missing.stderr.txt").exists())

    def test_timeout_output_is_decoded_before_writing(self):
        task = ReconTask(name="slow", category="SMB", command=["slow-tool"])
        timeout = subprocess.TimeoutExpired(task.command, 1, output=b"partial", stderr=b"stalled")
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
            with patch("basixenum.runner.subprocess.run", side_effect=timeout):
                result = run_task(task, Path(tmp))
            self.assertEqual(result.returncode, -1)
            self.assertEqual(result.stdout, "partial")
            self.assertIn("[TIMEOUT]", result.stderr)


if __name__ == "__main__":
    unittest.main()

