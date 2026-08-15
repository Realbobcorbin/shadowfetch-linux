"""Regression tests for first-boot graphics and status presentation."""

import ast
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "packages" / "shadowfetch-welcome" / "src" / "shadowfetch-welcome"
TEXT = SOURCE.read_text(encoding="utf-8")
TREE = ast.parse(TEXT, filename=str(SOURCE))
HELPERS = {"detect_display_vendor", "strip_terminal_escapes"}
NODES = [
    node
    for node in TREE.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in HELPERS
]
NAMESPACE = {"re": re}
exec(compile(ast.Module(body=NODES, type_ignores=[]), str(SOURCE), "exec"), NAMESPACE)


class WelcomeRegressionTests(unittest.TestCase):
    def test_virtio_display_is_virtual_not_amd(self):
        output = "0000:00:03.0 0300: 1af4:1050 (rev 01)"
        self.assertEqual("virtual", NAMESPACE["detect_display_vendor"](output))

    def test_numeric_amd_and_hybrid_nvidia_detection(self):
        detect = NAMESPACE["detect_display_vendor"]
        self.assertEqual("amd", detect("0000:03:00.0 0300: 1002:73bf"))
        self.assertEqual(
            "nvidia",
            detect(
                "0000:00:02.0 0300: 8086:46a6\n"
                "0000:01:00.0 0302: 10de:2c02"
            ),
        )

    def test_terminal_colour_sequences_are_removed(self):
        clean = NAMESPACE["strip_terminal_escapes"](
            "\x1b[1;31m!!\x1b[0m Buzz needs more disk space.\r"
        )
        self.assertEqual("!! Buzz needs more disk space.", clean)

    def test_virtual_renderer_copy_is_explicit(self):
        self.assertIn("Virtual machine uses software rendering", TEXT)
        self.assertIn('["lspci", "-Dn"]', TEXT)
        self.assertIn("strip_terminal_escapes(line.rstrip", TEXT)


if __name__ == "__main__":
    unittest.main()
