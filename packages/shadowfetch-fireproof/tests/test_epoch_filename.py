"""Cache filename derivation: apt encodes the epoch into the archive name.

/var/cache/apt/archives files are named with QuoteString(version, "_:"),
so 1:2.5-1 is stored as 1%3a2.5-1 - the pool basename (which drops the
epoch) must never be used.
"""
import unittest

from stubs import load_fireproofd

fp = load_fireproofd()


class TestAptQuote(unittest.TestCase):
    def test_epoch_colon_is_percent_encoded_lowercase(self):
        self.assertEqual(fp.apt_quote("1:2.5-1"), "1%3a2.5-1")

    def test_plain_version_passes_through(self):
        self.assertEqual(fp.apt_quote("5.2.15-2+b2"), "5.2.15-2+b2")

    def test_tilde_kept(self):
        self.assertEqual(fp.apt_quote("1.0~rc1-1"), "1.0~rc1-1")

    def test_percent_sign_is_self_encoded(self):
        self.assertEqual(fp.apt_quote("50%"), "50%25")

    def test_underscore_encoded(self):
        self.assertEqual(fp.apt_quote("a_b"), "a%5fb")


class TestCachedDebPath(unittest.TestCase):
    def test_epoch_versioned_package(self):
        self.assertEqual(
            fp.cached_deb_path("libjpeg62-turbo", "1:2.1.5-3", "amd64"),
            "/var/cache/apt/archives/libjpeg62-turbo_1%3a2.1.5-3_amd64.deb")

    def test_epoch_from_finding_example(self):
        self.assertEqual(
            fp.cached_deb_path("foo", "1:2.5-1", "amd64"),
            "/var/cache/apt/archives/foo_1%3a2.5-1_amd64.deb")

    def test_no_epoch(self):
        self.assertEqual(
            fp.cached_deb_path("bash", "5.2.15-2+b2", "amd64"),
            "/var/cache/apt/archives/bash_5.2.15-2+b2_amd64.deb")

    def test_arch_all(self):
        self.assertEqual(
            fp.cached_deb_path("shadowfetch-fireproof", "2.1.2-1", "all"),
            "/var/cache/apt/archives/shadowfetch-fireproof_2.1.2-1_all.deb")


if __name__ == "__main__":
    unittest.main()
