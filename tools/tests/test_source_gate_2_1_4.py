"""Unit tests for the Shadowfetch 2.1.4 source gate."""

import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "tools" / "source_gate_2_1_4.py"
_loader = importlib.machinery.SourceFileLoader("source_gate_test", str(SRC))
_spec = importlib.util.spec_from_loader("source_gate_test", _loader)
source_gate = importlib.util.module_from_spec(_spec)
_loader.exec_module(source_gate)


class SourceGateTests(unittest.TestCase):
    def test_build_time_downloader_entry_parser_ignores_comments(self):
        content = """
        # libdvd-pkg is intentionally omitted
        bash
        libdvd-pkg # this active entry must fail
        """
        self.assertEqual(
            ["libdvd-pkg"],
            source_gate.forbidden_build_time_downloader_entries(content),
        )


if __name__ == "__main__":
    unittest.main()
