"""NVIDIA telemetry tests that require no NVIDIA driver or bindings."""

import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest


HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "usr" / "libexec" / "firewatchd"
CONTROL = HERE.parent / "debian" / "control"
_loader = importlib.machinery.SourceFileLoader("firewatchd_nvidia_test", str(SRC))
_spec = importlib.util.spec_from_loader("firewatchd_nvidia_test", _loader)
firewatchd = importlib.util.module_from_spec(_spec)
_loader.exec_module(firewatchd)


class NvidiaSmiTests(unittest.TestCase):
    def test_package_does_not_pull_nvml_bindings_or_driver_libraries(self):
        binary_stanza = CONTROL.read_text().split("Description:", 1)[0]
        self.assertNotIn("python3-pynvml", binary_stanza)
        self.assertNotIn("libnvidia-", binary_stanza)

    def test_gpu_csv_normalizes_metrics_and_unsupported_values(self):
        rows = firewatchd.parse_nvidia_smi_gpus(
            "NVIDIA GeForce RTX 5080, 87, 16304, 4096, 72, N/A, 244.50\n"
        )
        self.assertEqual(1, len(rows))
        self.assertEqual("nvidia-smi", rows[0]["source"])
        self.assertEqual(87.0, rows[0]["busy_pct"])
        self.assertEqual(16304 * 1024 * 1024, rows[0]["vram_total_bytes"])
        self.assertEqual(4096 * 1024 * 1024, rows[0]["vram_used_bytes"])
        self.assertEqual(72.0, rows[0]["temp_c"])
        self.assertIsNone(rows[0]["fan_pct"])
        self.assertEqual(244.5, rows[0]["power_w"])

    def test_bad_rows_degrade_to_empty(self):
        self.assertEqual([], firewatchd.parse_nvidia_smi_gpus("not,csv\n"))
        self.assertEqual([], firewatchd.parse_nvidia_smi_gpus(None))

    def test_probe_is_bounded_and_legacy_throttle_field_falls_back(self):
        calls = []

        def runner(argv, **kwargs):
            calls.append((argv, kwargs))
            query = argv[1]
            if query == "--query-gpu=" + firewatchd.NVIDIA_GPU_QUERY:
                return SimpleNamespace(
                    returncode=0,
                    stdout=b"NVIDIA RTX, 10, 8192, 1024, 50, 30, 90\n",
                )
            if query == "--query-gpu=clocks_event_reasons.active":
                return SimpleNamespace(returncode=1, stdout=b"")
            return SimpleNamespace(returncode=0, stdout=b"0x0000000000000008\n")

        probe = firewatchd.Nvml.__new__(firewatchd.Nvml)
        probe.runner = runner
        probe.smi_path = firewatchd.NVIDIA_SMI
        probe.smi = firewatchd.NVIDIA_SMI
        probe._throttle_field = None
        probe._last_throttle_mask = 0
        probe._last_probe = 0.0
        self.assertEqual(1, len(probe.gpus()))
        self.assertEqual(8, probe.throttle_reasons())
        self.assertEqual("clocks_throttle_reasons.active", probe._throttle_field)
        self.assertTrue(all(call[1]["timeout"] == 3 for call in calls))
        self.assertTrue(all(call[0][0] == "/usr/bin/nvidia-smi" for call in calls))

    def test_timeout_degrades_without_stale_telemetry(self):
        def timeout(*_args, **_kwargs):
            raise subprocess.TimeoutExpired("nvidia-smi", 3)

        probe = firewatchd.Nvml.__new__(firewatchd.Nvml)
        probe.runner = timeout
        probe.smi_path = firewatchd.NVIDIA_SMI
        probe.smi = firewatchd.NVIDIA_SMI
        probe._throttle_field = None
        probe._last_throttle_mask = 16
        probe._last_probe = 0.0
        self.assertEqual([], probe.gpus())
        self.assertEqual(0, probe.throttle_reasons())


if __name__ == "__main__":
    unittest.main()
