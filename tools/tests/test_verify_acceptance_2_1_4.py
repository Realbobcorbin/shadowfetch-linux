from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "verify_acceptance_2_1_4.py"
SPEC = importlib.util.spec_from_file_location("verify_acceptance_2_1_4", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
qa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qa)


def base_manifest() -> dict:
    return {
        "schema_version": 1,
        "release": {
            "version": "2.1.4",
            "edition": "Fire Edition",
            "codename": "Umbra",
        },
        "evidence_root": "work/qa-2.1.4/evidence",
        "artifact": {},
        "cases": [
            {
                "id": "PRE-01",
                "phase": "prepublish",
                "area": "test",
                "title": "Pre-publication test",
                "required": True,
                "status": "pending",
                "evidence": [],
                "notes": "",
            },
            {
                "id": "POST-01",
                "phase": "postpublish",
                "area": "test",
                "title": "Post-publication test",
                "required": True,
                "status": "pending",
                "evidence": [],
                "notes": "",
            },
        ],
    }


def png_header(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height)


class AcceptanceVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "Makefile").write_text("test:\n\t@true\n", encoding="utf-8")
        (self.root / "packages").mkdir()
        self.manifest = self.root / "qa" / "2.1.4" / "acceptance.json"
        self.manifest.parent.mkdir(parents=True)
        self.evidence_root = self.root / "work" / "qa-2.1.4" / "evidence"
        self.evidence_root.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_manifest(self, data: dict) -> None:
        self.manifest.write_text(json.dumps(data), encoding="utf-8")

    def verify(self, phase: str = "prepublish", allow_pending: bool = True) -> int:
        return qa.verify(
            argparse.Namespace(
                manifest=self.manifest,
                phase=phase,
                allow_pending=allow_pending,
            )
        )

    def test_pending_manifest_structure_can_be_audited(self) -> None:
        self.write_manifest(base_manifest())
        self.assertEqual(self.verify(), 0)

    def test_duplicate_case_id_is_rejected(self) -> None:
        data = base_manifest()
        data["cases"][1]["id"] = data["cases"][0]["id"]
        self.assertIn("duplicate case id", " ".join(qa.validate_manifest(data)))

    def test_evidence_path_cannot_escape_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "escapes evidence root"):
            qa.resolve_evidence(self.evidence_root, "../outside.log")

    def test_passing_case_requires_evidence(self) -> None:
        data = base_manifest()
        data["cases"][0]["status"] = "pass"
        self.write_manifest(data)
        self.assertEqual(self.verify(), 1)

    def test_tampered_evidence_is_rejected(self) -> None:
        data = base_manifest()
        evidence = self.evidence_root / "result.log"
        evidence.write_text("original", encoding="utf-8")
        data["cases"][0]["status"] = "pass"
        data["cases"][0]["evidence"] = [
            {"kind": "log", "path": evidence.name, "sha256": "0" * 64}
        ]
        self.write_manifest(data)
        self.assertEqual(self.verify(), 1)

    def test_small_screenshot_is_rejected(self) -> None:
        data = base_manifest()
        evidence = self.evidence_root / "small.png"
        evidence.write_bytes(png_header(1024, 600))
        data["cases"][0]["status"] = "pass"
        data["cases"][0]["evidence"] = [
            {
                "kind": "screenshot",
                "path": evidence.name,
                "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
            }
        ]
        self.write_manifest(data)
        self.assertEqual(self.verify(), 1)

    def test_full_size_screenshot_with_matching_hash_passes(self) -> None:
        data = base_manifest()
        evidence = self.evidence_root / "desktop.png"
        evidence.write_bytes(png_header(1280, 720))
        data["cases"][0]["status"] = "pass"
        data["cases"][0]["evidence"] = [
            {
                "kind": "screenshot",
                "path": evidence.name,
                "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
            }
        ]
        self.write_manifest(data)
        self.assertEqual(self.verify(), 0)

    def test_final_phase_includes_postpublication_cases(self) -> None:
        data = base_manifest()
        data["cases"][0]["required"] = False
        data["artifact"] = {
            "iso_path": "shadowfetch-2.1.4-amd64.iso",
            "iso_sha256": "a" * 64,
            "iso_size_bytes": 1,
            "signature_path": "shadowfetch-2.1.4-amd64.iso.asc",
            "signing_fingerprint": "8F13CE1535EE1F4A2916A1F73C5C900B7BE80CA1",
            "evidence_bundle_path": "shadowfetch-2.1.4-qa.tar.zst",
            "evidence_bundle_sha256": "b" * 64,
        }
        self.write_manifest(data)
        self.assertEqual(self.verify(phase="prepublish", allow_pending=False), 0)
        self.assertEqual(self.verify(phase="final", allow_pending=False), 1)

    def test_record_pass_requires_file_and_hashes_it(self) -> None:
        data = base_manifest()
        self.write_manifest(data)
        evidence = self.evidence_root / "suite.log"
        evidence.write_text("97 tests passed\n", encoding="utf-8")
        result = qa.record(
            argparse.Namespace(
                manifest=self.manifest,
                case_id="PRE-01",
                status="pass",
                evidence=[evidence],
                kind="log",
                notes="fresh run",
                clear_evidence=False,
            )
        )
        self.assertEqual(result, 0)
        recorded = json.loads(self.manifest.read_text(encoding="utf-8"))
        case = recorded["cases"][0]
        self.assertEqual(case["status"], "pass")
        self.assertEqual(case["notes"], "fresh run")
        self.assertEqual(case["evidence"][0]["sha256"], qa.sha256_file(evidence))


if __name__ == "__main__":
    unittest.main()
