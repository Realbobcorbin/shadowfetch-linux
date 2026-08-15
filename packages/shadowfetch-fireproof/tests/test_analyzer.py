"""Analyzer diff logic: library-rename pairing, stems, change-set hash."""
import unittest
from types import SimpleNamespace

from stubs import load_fireproofd

fp = load_fireproofd()


def _entry(name, installed=None, candidate=None, red=False):
    return {"name": name, "installed": installed, "candidate": candidate,
            "red": red}


class TestLibStem(unittest.TestCase):
    def test_t64_suffix_and_soname_digits(self):
        self.assertEqual(fp._lib_stem("libfoo1t64"), "libfoo")
        self.assertEqual(fp._lib_stem("libfoo1"), "libfoo")

    def test_trailing_soname_dashes_and_dots_stripped(self):
        self.assertEqual(fp._lib_stem("libssl3.0"), "libssl")
        self.assertEqual(fp._lib_stem("libtiff-6"), "libtiff")

    def test_word_suffix_is_not_a_soname(self):
        # A name that does not END in soname digits keeps its full stem:
        # libjpeg62-turbo must not pair with plain libjpeg renames.
        self.assertEqual(fp._lib_stem("libjpeg62-turbo"), "libjpeg62-turbo")


class TestPairLibraryRenames(unittest.TestCase):
    def test_t64_transition_collapses_to_one_rename(self):
        installs = [_entry("libfoo1t64", candidate="1.2-3")]
        removals = [_entry("libfoo1", installed="1.2-2")]
        renames, installs, removals = fp.pair_library_renames(
            installs, removals)
        self.assertEqual(len(renames), 1)
        self.assertEqual(renames[0]["from"], "libfoo1")
        self.assertEqual(renames[0]["to"], "libfoo1t64")
        self.assertEqual(renames[0]["version"], "1.2-3")
        self.assertEqual(renames[0]["note"], "same library, new name")
        self.assertEqual(installs, [])
        self.assertEqual(removals, [])

    def test_soname_bump_pairs(self):
        installs = [_entry("libbar2", candidate="2.0-1")]
        removals = [_entry("libbar1", installed="1.9-4")]
        renames, installs, removals = fp.pair_library_renames(
            installs, removals)
        self.assertEqual([(r["from"], r["to"]) for r in renames],
                         [("libbar1", "libbar2")])
        self.assertEqual(installs, [])
        self.assertEqual(removals, [])

    def test_non_library_packages_never_pair(self):
        installs = [_entry("firefox2", candidate="2.0")]
        removals = [_entry("firefox1", installed="1.0")]
        renames, installs2, removals2 = fp.pair_library_renames(
            installs, removals)
        self.assertEqual(renames, [])
        self.assertEqual(len(installs2), 1)
        self.assertEqual(len(removals2), 1)

    def test_identical_name_never_pairs_with_itself(self):
        installs = [_entry("libbaz1", candidate="1.1")]
        removals = [_entry("libbaz1", installed="1.0")]
        renames, installs2, removals2 = fp.pair_library_renames(
            installs, removals)
        self.assertEqual(renames, [])
        self.assertEqual(len(installs2), 1)
        self.assertEqual(len(removals2), 1)

    def test_each_removal_consumed_at_most_once(self):
        installs = [_entry("libqux2", candidate="2.0"),
                    _entry("libqux2t64", candidate="2.0")]
        removals = [_entry("libqux1", installed="1.0")]
        renames, installs2, removals2 = fp.pair_library_renames(
            installs, removals)
        self.assertEqual(len(renames), 1)
        self.assertEqual(removals2, [])
        self.assertEqual(len(installs2), 1)   # the unpaired install stays

    def test_unrelated_stems_do_not_pair(self):
        installs = [_entry("libssl3", candidate="3.0")]
        removals = [_entry("libzstd1", installed="1.5")]
        renames, installs2, removals2 = fp.pair_library_renames(
            installs, removals)
        self.assertEqual(renames, [])
        self.assertEqual(len(installs2), 1)
        self.assertEqual(len(removals2), 1)


class _Pkg(SimpleNamespace):
    pass


def _pkg(name, installed=None, candidate=None, delete=False):
    return _Pkg(
        name=name,
        marked_delete=delete,
        installed=SimpleNamespace(version=installed) if installed else None,
        candidate=SimpleNamespace(version=candidate) if candidate else None)


class TestChangeSetHash(unittest.TestCase):
    def test_order_independent(self):
        a = [_pkg("zsh", installed="5.9-4", candidate="5.9-5"),
             _pkg("bash", installed="5.2-1", candidate="5.2-2")]
        b = list(reversed(a))
        self.assertEqual(fp.change_set_hash(a), fp.change_set_hash(b))

    def test_remove_differs_from_install(self):
        inst = [_pkg("libfoo1", installed="1.0", candidate="1.1")]
        remv = [_pkg("libfoo1", installed="1.0", candidate="1.1",
                     delete=True)]
        self.assertNotEqual(fp.change_set_hash(inst),
                            fp.change_set_hash(remv))

    def test_version_change_changes_hash(self):
        one = [_pkg("bash", installed="5.2-1", candidate="5.2-2")]
        two = [_pkg("bash", installed="5.2-1", candidate="5.2-3")]
        self.assertNotEqual(fp.change_set_hash(one), fp.change_set_hash(two))


if __name__ == "__main__":
    unittest.main()
