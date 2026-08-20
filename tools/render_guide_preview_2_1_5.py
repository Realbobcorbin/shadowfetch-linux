#!/usr/bin/env python3
"""Render deterministic Shadowfetch Guide screenshots for release QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROL_CENTER = (
    ROOT
    / "packages/shadowfetch-control-center/data/usr/share/shadowfetch/control-center"
)


def fixture() -> dict:
    def check(
        label: str,
        status: str,
        status_label: str,
        summary: str,
        source: str,
        route: str | None = None,
        action: str | None = None,
    ) -> dict:
        item = {
            "label": label,
            "status": status,
            "status_label": status_label,
            "summary": summary,
            "source": source,
        }
        if route and action:
            item.update({"route": route, "action": action})
        return item

    return {
        "schema_version": 1,
        "passport_version": "1.0",
        "release_version": "2.1.5",
        "generated_at": "2026-08-18T18:30:00Z",
        "context": {
            "mode": "live-session",
            "operating_system": "Shadowfetch Linux 2.1.5",
            "architecture": "x86_64",
        },
        "capabilities": {
            "camera_count": 1,
            "bluetooth_controller_count": 1,
            "wireless_adapter_count": 1,
        },
        "verdict": {
            "status": "ready-with-notes",
            "title": "This computer is ready with one note",
            "summary": (
                "Core desktop hardware is working. Install the recommended NVIDIA "
                "driver after setup for full graphics and local AI performance."
            ),
            "attention_count": 0,
            "note_count": 1,
        },
        "checks": [
            check(
                "Boot compatibility",
                "ready",
                "Ready",
                "UEFI boot is available and Secure Boot is disabled.",
                "local firmware probe",
            ),
            check(
                "Graphics",
                "note",
                "Driver recommended",
                "The NVIDIA GPU is detected; the open driver can be installed safely after setup.",
                "PCI and kernel driver probes",
                "drivers",
                "Open Drivers",
            ),
            check(
                "Network",
                "ready",
                "Connected",
                "A physical network adapter has an active link.",
                "local link-state probe",
            ),
            check(
                "Audio",
                "ready",
                "Ready",
                "The audio session and output devices are available.",
                "PipeWire session probe",
            ),
            check(
                "Drivers and firmware",
                "ready",
                "Ready",
                "No missing firmware was reported by the current boot.",
                "kernel log and package state",
            ),
            check(
                "Memory",
                "ready",
                "32 GB available",
                "There is enough memory for the desktop and recommended local models.",
                "local memory probe",
            ),
            check(
                "Install storage",
                "ready",
                "Ready",
                "The largest destination disk has more than 100 GB available.",
                "local block-device totals",
            ),
            check(
                "Recovery",
                "ready",
                "Available",
                "Phoenix recovery and Fireproof rollback tools are installed.",
                "installed Shadowfetch components",
                "phoenix",
                "Open Recover",
            ),
            check(
                "Local AI",
                "ready",
                "Buzz ready",
                "Buzz can guide model selection after installation; no model is forced on you.",
                "hardware profile and installed components",
                "agents",
                "Open Local AI",
            ),
        ],
        "privacy": {
            "local_only": True,
            "upload_performed": False,
            "omitted": [
                "hostname",
                "account name",
                "network identifiers",
                "serial numbers",
                "filesystem identifiers",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()

    if args.width < 1000 or args.height < 660:
        parser.error("Control Center screenshots must be at least 1000x660")

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")
    sys.path.insert(0, str(CONTROL_CENTER))

    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QApplication
    from sfcc import busutil
    from sfcc.app import ControlCenterWindow

    app = QApplication.instance() or QApplication([])
    app.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
    busutil.sf_version = lambda: "2.1.5"
    busutil.system_summary = lambda: ("System ready", "No failed services")
    busutil.fireproof_updates = lambda: 0
    window = ControlCenterWindow()
    guide = window.pages[0]
    guide._started = True
    guide._document = fixture()
    guide.save_button.setEnabled(True)
    guide._render(guide._document)

    window.resize(args.width, args.height)
    window.show()
    for _ in range(4):
        app.processEvents()

    image = window.grab().toImage()
    if image.isNull() or image.width() != args.width or image.height() != args.height:
        raise RuntimeError(
            f"unexpected capture size: {image.width()}x{image.height()}"
        )

    sample = image.scaled(240, 150)
    colors = {
        sample.pixelColor(x, y).rgba()
        for y in range(sample.height())
        for x in range(sample.width())
    }
    if len(colors) < 40:
        raise RuntimeError(f"capture appears blank or visually flat: {len(colors)} colors")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(args.output), "PNG"):
        raise RuntimeError(f"could not save {args.output}")
    print(
        f"GUIDE_RENDER_PASSED path={args.output} "
        f"size={image.width()}x{image.height()} sampled_colors={len(colors)}"
    )
    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
