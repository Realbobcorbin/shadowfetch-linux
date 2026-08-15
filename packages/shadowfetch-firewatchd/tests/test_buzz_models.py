"""Safety and compatibility tests for Buzz model discovery."""

import importlib.machinery
import importlib.util
import json
import pathlib
import unittest


HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "usr" / "libexec" / "firewatchd"

_loader = importlib.machinery.SourceFileLoader("firewatchd_test", str(SRC))
_spec = importlib.util.spec_from_loader("firewatchd_test", _loader)
firewatchd = importlib.util.module_from_spec(_spec)
_loader.exec_module(firewatchd)


class TestBuzzModelWatcher(unittest.TestCase):
    def parse(self, payload):
        return firewatchd.BuzzModelWatcher._parse(
            json.dumps(payload).encode("utf-8"))

    def test_endpoint_is_fixed_to_loopback(self):
        self.assertEqual(
            firewatchd.BuzzModelWatcher.URL,
            "http://127.0.0.1:9337/v1/models",
        )
        self.assertEqual(firewatchd.HTTP_TIMEOUT_S, 1.0)
        self.assertLessEqual(firewatchd.HTTP_BODY_CAP, 262144)

    def test_openai_model_list_is_normalized(self):
        self.assertEqual(
            self.parse({"data": [{"id": "org/model:Q4_K_M"}]}),
            [{
                "runtime": "buzz-mesh",
                "name": "org/model:Q4_K_M",
                "model": "org/model:Q4_K_M",
                "state": "available",
                "port": 9337,
            }],
        )

    def test_malformed_and_control_character_ids_are_ignored(self):
        payload = {"data": [
            None,
            {},
            {"id": 7},
            {"id": ""},
            {"id": "bad\nmodel"},
            {"id": "x" * 257},
            {"id": " good/model "},
        ]}
        rows = self.parse(payload)
        self.assertEqual([row["name"] for row in rows], ["good/model"])

    def test_malformed_documents_degrade_to_empty(self):
        for body in (b"", b"not-json", b"[]", b'{"data":{}}'):
            with self.subTest(body=body):
                self.assertEqual(firewatchd.BuzzModelWatcher._parse(body), [])

    def test_published_inventory_is_capped(self):
        rows = self.parse({"data": [{"id": f"model-{i}"} for i in range(100)]})
        self.assertEqual(len(rows), 64)
        self.assertEqual(rows[-1]["name"], "model-63")

    def test_failed_poll_clears_stale_inventory(self):
        watcher = firewatchd.BuzzModelWatcher()
        watcher.models = [{"name": "stale"}]
        original = firewatchd.BuzzModelWatcher._http_get
        firewatchd.BuzzModelWatcher._http_get = staticmethod(lambda: None)
        try:
            self.assertEqual(watcher.poll(), [])
            self.assertEqual(watcher.models, [])
            self.assertEqual(watcher.jobs(), [])
        finally:
            firewatchd.BuzzModelWatcher._http_get = staticmethod(original)


if __name__ == "__main__":
    unittest.main()
