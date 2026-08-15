#!/usr/bin/env python3
"""Reproducible source and secret gate for Shadowfetch Linux 2.1.4."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PREFIXES = (
    "build/",
    "repo/",
    "work/",
    "live-build/binary/",
    "live-build/cache/",
    "live-build/chroot/",
)
ACTIVE_IMAGE_ROOTS = (
    "packages/shadowfetch-defaults/data",
    "packages/shadowfetch-welcome/src/shadowfetch-welcome",
    "packages/shadowfetch-control-center/data",
    "live-build/config/includes.chroot",
    "live-build/config/package-lists",
)
RETIRED_RUNTIME = re.compile(
    r"openclaw|\bhermes\b|\bollama\b|open[- ]?webui|llama\.cpp|llama-server",
    re.IGNORECASE,
)
MIGRATION_MANIFEST = (
    "packages/shadowfetch-defaults/data/usr/share/shadowfetch/"
    "migrations/2.1.3-ai-packages"
)
EXPECTED_MIGRATION_PACKAGES = (
    "shadowfetch-ai-workspace",
    "llama.cpp",
    "llama.cpp-services",
    "llama.cpp-tools",
    "llama.cpp-tools-extra",
    "libllama0",
    "whisper.cpp",
    "libwhisper1",
    "whisper.cpp-tools",
)
FORBIDDEN_BUILD_TIME_DOWNLOADERS = frozenset({"libdvd-pkg"})


def run(label: str, command: list[str], *, cwd: Path = ROOT) -> None:
    print(f"\n>>> {label}")
    subprocess.run(command, cwd=cwd, check=True)
    print(f"PASS: {label}")


def candidate_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    candidates: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = os.fsdecode(raw)
        if relative.startswith(BLOCKED_PREFIXES):
            continue
        path = ROOT / relative
        if path.is_file():
            candidates.append(path)
    return sorted(set(candidates))


def first_line(path: Path) -> str:
    try:
        with path.open("rb") as handle:
            return handle.readline(512).decode("utf-8", "replace").strip()
    except OSError:
        return ""


def shell_files(candidates: list[Path]) -> tuple[list[Path], list[Path]]:
    owned: list[Path] = []
    vendored: list[Path] = []
    for path in candidates:
        relative = path.relative_to(ROOT)
        if not relative.parts or relative.parts[0] not in {"live-build", "packages", "tools"}:
            continue
        line = first_line(path)
        if not line.startswith("#!"):
            continue
        if not re.search(r"(?:^|/|\s)(?:ba|da|k|z)?sh(?:\s|$)", line):
            continue
        if relative.parts[:2] == ("packages", "grub-btrfs"):
            vendored.append(path)
        else:
            owned.append(path)
    return owned, vendored


def parser_gates(candidates: list[Path]) -> None:
    python_files: list[Path] = []
    json_files: list[Path] = []
    xml_files: list[Path] = []
    desktop_files: list[Path] = []
    for path in candidates:
        line = first_line(path)
        if path.suffix == ".py" or (line.startswith("#!") and "python" in line):
            python_files.append(path)
        if path.suffix == ".json":
            json_files.append(path)
        if path.suffix in {".menu", ".xml"}:
            xml_files.append(path)
        if path.suffix == ".desktop" and (
            "applications" in path.parts
            or "autostart" in path.parts
            or path.name == "shadowfetch-welcome.desktop"
        ):
            desktop_files.append(path)

    for path in python_files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print(f"PASS: Python parse ({len(python_files)} files)")

    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))
    print(f"PASS: JSON parse ({len(json_files)} files)")

    for path in xml_files:
        ET.parse(path)
    print(f"PASS: XML/menu parse ({len(xml_files)} files)")

    if not shutil.which("desktop-file-validate"):
        raise RuntimeError("desktop-file-validate is required")
    if desktop_files:
        run(
            f"desktop entry validation ({len(desktop_files)} files)",
            ["desktop-file-validate", *map(str, desktop_files)],
        )


def secret_gates(candidates: list[Path]) -> None:
    if not shutil.which("gitleaks"):
        raise RuntimeError("gitleaks is required")
    with tempfile.TemporaryDirectory(prefix="shadowfetch-source-gate-") as temporary:
        mirror = Path(temporary)
        for source in candidates:
            relative = source.relative_to(ROOT)
            destination = mirror / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        run(
            f"Gitleaks candidate tree ({len(candidates)} files)",
            [
                "gitleaks",
                "dir",
                ".",
                "--no-banner",
                "--no-color",
                "--redact",
                "--config",
                str(mirror / ".gitleaks.toml"),
            ],
            cwd=mirror,
        )
    run(
        "Gitleaks Git history",
        [
            "gitleaks",
            "git",
            ".",
            "--no-banner",
            "--no-color",
            "--redact",
            "--config",
            str(ROOT / ".gitleaks.toml"),
        ],
    )


def retired_runtime_gate() -> None:
    findings: list[str] = []
    for value in ACTIVE_IMAGE_ROOTS:
        root = ROOT / value
        paths = [root] if root.is_file() else root.rglob("*")
        for path in paths:
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.relative_to(ROOT).as_posix() == MIGRATION_MANIFEST:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if RETIRED_RUNTIME.search(content):
                findings.append(path.relative_to(ROOT).as_posix())
    if findings:
        raise RuntimeError(
            "retired runtime references remain in the active image: "
            + ", ".join(sorted(findings))
        )
    print("PASS: retired OpenClaw, Hermes and competing runtime scan")


def migration_manifest_gate() -> None:
    path = ROOT / MIGRATION_MANIFEST
    packages = tuple(path.read_text(encoding="utf-8").splitlines())
    if packages != EXPECTED_MIGRATION_PACKAGES:
        raise RuntimeError(
            "2.1.3 migration manifest differs from the reviewed package set"
        )
    if len(packages) != len(set(packages)):
        raise RuntimeError("2.1.3 migration manifest contains duplicates")
    print("PASS: exact 2.1.3 retired-package migration manifest")


def forbidden_build_time_downloader_entries(content: str) -> list[str]:
    entries: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.partition("#")[0].strip()
        if not line:
            continue
        package = line.split()[0]
        if package in FORBIDDEN_BUILD_TIME_DOWNLOADERS:
            entries.add(package)
    return sorted(entries)


def build_time_downloader_gate() -> None:
    findings: list[str] = []
    package_lists = ROOT / "live-build" / "config" / "package-lists"
    for path in sorted(package_lists.glob("*.list.chroot")):
        blocked = forbidden_build_time_downloader_entries(
            path.read_text(encoding="utf-8")
        )
        findings.extend(
            f"{path.relative_to(ROOT).as_posix()}:{package}" for package in blocked
        )
    if findings:
        raise RuntimeError(
            "packages with unpinned build-time downloads remain in the image: "
            + ", ".join(findings)
        )
    print("PASS: no package-list entries with unpinned build-time downloads")


def main() -> int:
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    candidates = candidate_files()
    if not candidates:
        raise RuntimeError("candidate source set is empty")
    apple_double = [path for path in candidates if path.name.startswith("._")]
    if apple_double:
        raise RuntimeError(
            "AppleDouble metadata files found: "
            + ", ".join(str(path.relative_to(ROOT)) for path in apple_double)
        )
    print(f"Shadowfetch Linux 2.1.4 source gate: {len(candidates)} candidate files")

    run("behavioral and unit tests", ["make", "test"])
    run("Git whitespace validation", ["git", "diff", "--check"])

    owned_shell, vendored_shell = shell_files(candidates)
    if not shutil.which("shellcheck"):
        raise RuntimeError("shellcheck is required")
    if owned_shell:
        run(
            f"ShellCheck Shadowfetch scripts ({len(owned_shell)} files)",
            ["shellcheck", "--severity=warning", "-x", *map(str, owned_shell)],
        )
    if vendored_shell:
        run(
            f"ShellCheck vendored scripts ({len(vendored_shell)} files)",
            ["shellcheck", "--severity=error", "-x", *map(str, vendored_shell)],
        )
    for path in (*owned_shell, *vendored_shell):
        shell = "bash" if "bash" in first_line(path) else "sh"
        subprocess.run([shell, "-n", str(path)], check=True)
    print(f"PASS: shell parser ({len(owned_shell) + len(vendored_shell)} files)")

    parser_gates(candidates)
    build_time_downloader_gate()
    secret_gates(candidates)
    migration_manifest_gate()
    retired_runtime_gate()
    print("\nSOURCE_GATE_PASSED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError, SyntaxError) as exc:
        print(f"SOURCE_GATE_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
