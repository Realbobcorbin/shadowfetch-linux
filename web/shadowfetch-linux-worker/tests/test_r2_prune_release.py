#!/usr/bin/env python3

from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from r2_prune_release import binary_pool_keys, source_pool_keys


class ReleaseIndexTests(unittest.TestCase):
    def test_binary_pool_keys(self) -> None:
        packages = """Package: shadowfetch-meta
Filename: pool/main/s/shadowfetch-meta/shadowfetch-meta_2.1.4-1_all.deb
"""
        self.assertEqual(
            binary_pool_keys(packages),
            {
                "apt/pool/main/s/shadowfetch-meta/"
                "shadowfetch-meta_2.1.4-1_all.deb"
            },
        )

    def test_source_pool_keys(self) -> None:
        sources = """Package: shadowfetch-meta
Directory: pool/main/s/shadowfetch-meta
Files:
 abc123 100 shadowfetch-meta_2.1.4-1.dsc
 def456 200 shadowfetch-meta_2.1.4.orig.tar.xz
 ghi789 300 shadowfetch-meta_2.1.4-1.debian.tar.xz
Checksums-Sha256:
 111aaa 100 shadowfetch-meta_2.1.4-1.dsc
"""
        self.assertEqual(
            source_pool_keys(sources),
            {
                "apt/pool/main/s/shadowfetch-meta/"
                "shadowfetch-meta_2.1.4-1.dsc",
                "apt/pool/main/s/shadowfetch-meta/"
                "shadowfetch-meta_2.1.4.orig.tar.xz",
                "apt/pool/main/s/shadowfetch-meta/"
                "shadowfetch-meta_2.1.4-1.debian.tar.xz",
            },
        )


if __name__ == "__main__":
    unittest.main()
