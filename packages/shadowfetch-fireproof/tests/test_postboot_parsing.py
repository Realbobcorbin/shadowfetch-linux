"""fireproof-postboot pre_point parsing, run against the REAL script line.

The extraction line is pulled out of the installed script text and
executed under sh with fixture flag files, so the test breaks if the
script's parsing ever drifts. The contract: a numeric pre_point parses
to its value; "pre_point": null or an absent key parses to EMPTY (no
fabricated Point 0 - snapshot 0 is snapper's "current" pseudo-snapshot,
never a restore target).
"""
import os
import subprocess
import unittest

from stubs import FIXTURES, POSTBOOT


def _extract_parse_line():
    with open(POSTBOOT) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("pre_point=$(sed"):
                return stripped
    raise AssertionError("pre_point parse line not found in %s" % POSTBOOT)


def _parse(fixture):
    line = _extract_parse_line()
    script = 'FLAG=%s\n%s\nprintf %%s "$pre_point"\n' % (
        os.path.join(FIXTURES, fixture), line)
    proc = subprocess.run(["sh", "-c", script], capture_output=True,
                          text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


class TestPrePointParsing(unittest.TestCase):
    def test_numeric_pre_point_parses(self):
        self.assertEqual(_parse("pending-numeric.json"), "42")

    def test_null_pre_point_parses_empty_never_zero(self):
        self.assertEqual(_parse("pending-null.json"), "")

    def test_absent_pre_point_parses_empty_never_zero(self):
        self.assertEqual(_parse("pending-absent.json"), "")

    def test_script_never_fabricates_point_zero(self):
        # The old bug: `[ -n "$pre_point" ] || pre_point=0` invented a
        # bogus Phoenix Point 0. Assert that fallback stays gone and the
        # empty case is routed to clear_flag instead.
        with open(POSTBOOT) as f:
            text = f.read()
        self.assertNotIn('pre_point=0', text)
        self.assertIn('if [ -z "$pre_point" ]', text)
        self.assertIn("clear_flag", text)

    def test_script_is_valid_sh(self):
        proc = subprocess.run(["sh", "-n", POSTBOOT], capture_output=True,
                              text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
