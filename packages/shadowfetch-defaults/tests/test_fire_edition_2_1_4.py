#!/usr/bin/env python3
"""Focused release gates for the 2.1.4 Buzz and graphics transition."""

from __future__ import annotations

import json
import os
import py_compile
import re
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULTS = ROOT / "packages" / "shadowfetch-defaults"
WELCOME = ROOT / "packages" / "shadowfetch-welcome" / "src" / "shadowfetch-welcome"
CONTROL = ROOT / "packages" / "shadowfetch-control-center" / "data"
PROVISION = DEFAULTS / "data/usr/libexec/shadowfetch-buzz-provision"
BUZZ = DEFAULTS / "data/usr/bin/shadowfetch-buzz"
BUZZ_BOOTSTRAP = DEFAULTS / "data/usr/libexec/shadowfetch-buzz-bootstrap"
BUZZ_STACK = DEFAULTS / "data/usr/libexec/shadowfetch-buzz-stack"
BUZZ_COMPOSE = DEFAULTS / "data/usr/share/shadowfetch/buzz/compose.yml"
MIGRATION_HELPER = DEFAULTS / "data/usr/libexec/shadowfetch-migrate-2.1.3-ai"
MIGRATION_MANIFEST = (
    DEFAULTS / "data/usr/share/shadowfetch/migrations/2.1.3-ai-packages"
)
PLYMOUTH = (
    ROOT
    / "packages/shadowfetch-branding/data/usr/share/plymouth/themes/"
    "shadowfetch/shadowfetch.script"
)


class FireEdition214Tests(unittest.TestCase):
    def test_release_version_and_package_versions_match(self):
        makefile = (ROOT / "Makefile").read_text()
        self.assertRegex(makefile, r"(?m)^VERSION\s+\?= 2\.1\.4$")
        for changelog in (ROOT / "packages").glob("shadowfetch-*/debian/changelog"):
            first = changelog.read_text().splitlines()[0]
            self.assertIn("(2.1.4-1)", first, changelog)

    def test_debian_revision_versions_use_quilt_source_format(self):
        formats = sorted((ROOT / "packages").glob("*/debian/source/format"))
        self.assertEqual(13, len(formats))
        for source_format in formats:
            self.assertEqual("3.0 (quilt)", source_format.read_text().strip())
        makefile = (ROOT / "Makefile").read_text()
        repo = makefile.split("repo: packages", 1)[1].split("\niso: repo", 1)[0]
        self.assertIn(".orig.tar.xz", repo)
        self.assertIn("--sort=name", repo)
        self.assertIn("dpkg-source -b $$pkg", repo)
        self.assertIn("debsign --no-conf -k$(REPO_KEY_ID)", repo)

    def test_retired_runtimes_are_absent_from_active_image_source(self):
        retired = re.compile(
            r"openclaw|\bhermes\b|\bollama\b|open[- ]?webui|llama\.cpp|llama-server",
            re.IGNORECASE,
        )
        roots = [
            DEFAULTS / "data",
            WELCOME,
            CONTROL,
            ROOT / "live-build" / "config" / "includes.chroot",
            ROOT / "live-build" / "config" / "package-lists",
        ]
        findings = []
        for root in roots:
            paths = [root] if root.is_file() else root.rglob("*")
            for path in paths:
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                if path == MIGRATION_MANIFEST:
                    continue
                flags = getattr(path.stat(), "st_flags", 0)
                if flags & getattr(stat, "SF_DATALESS", 0):
                    continue
                try:
                    content = path.read_text()
                except UnicodeDecodeError:
                    continue
                if retired.search(content):
                    findings.append(str(path.relative_to(ROOT)))
        self.assertEqual([], findings)

    def test_competing_model_helpers_and_package_are_removed(self):
        for path in (
            DEFAULTS / "data/usr/bin/shadowfetch-ai",
            DEFAULTS / "data/usr/bin/shadowfetch-assistant",
            DEFAULTS / "data/usr/bin/shadowfetch-llm",
            DEFAULTS / "data/usr/libexec/shadowfetch-ai-provision",
            DEFAULTS / "data/usr/share/applications/shadowfetch-ai.desktop",
            DEFAULTS / "data/usr/share/applications/shadowfetch-ai-webui.desktop",
            DEFAULTS / "data/usr/share/applications/shadowfetch-assistant.desktop",
            DEFAULTS / "data/usr/share/applications/shadowfetch-llm.desktop",
            ROOT / "live-build/config/includes.chroot/usr/local/share/applications/"
            "shadowfetch-local-ai.desktop",
            ROOT / "live-build/config/includes.chroot/usr/share/desktop-directories/"
            "shadowfetch-ai.directory",
            ROOT / "live-build/config/includes.chroot/usr/local/share/applications/"
            "shadowfetch-control-center.desktop",
            ROOT / "live-build/config/includes.chroot/usr/local/share/applications/"
            "shadowfetch-welcome.desktop",
            DEFAULTS / "data/etc/systemd/system/ollama.service.d/10-localhost.conf",
            ROOT / "packages/shadowfetch-ai-workspace",
        ):
            self.assertFalse(path.exists(), path)
        self.assertNotIn("shadowfetch-ai-workspace", (ROOT / "Makefile").read_text())
        self.assertEqual(
            [
                "shadowfetch-ai-workspace",
                "llama.cpp",
                "llama.cpp-services",
                "llama.cpp-tools",
                "llama.cpp-tools-extra",
                "libllama0",
                "whisper.cpp",
                "libwhisper1",
                "whisper.cpp-tools",
            ],
            MIGRATION_MANIFEST.read_text().splitlines(),
        )

    def test_repo_is_rebuilt_from_an_exact_package_allowlist(self):
        makefile = (ROOT / "Makefile").read_text()
        repo = makefile.split("repo: packages", 1)[1].split("\niso: repo", 1)[0]
        self.assertIn("rm -rf $(REPO_DIR)/db $(REPO_DIR)/dists $(REPO_DIR)/pool", repo)
        self.assertIn('"$$tmp/expected-binary" "$$tmp/actual-binary"', repo)
        self.assertIn('"$$tmp/expected-source" "$$tmp/actual-source"', repo)
        self.assertIn("Repo allowlist passed", repo)

    def test_iso_build_is_fresh_and_propagates_live_build_failures(self):
        makefile = (ROOT / "Makefile").read_text()
        iso = makefile.split("\niso: repo", 1)[1].split("\n# Detached GPG", 1)[0]
        self.assertIn(
            "rm -f $(ROOT)/$(ISO_NAME) $(ROOT)/$(ISO_NAME).sha256 "
            "$(ROOT)/$(ISO_NAME).asc",
            iso,
        )
        self.assertIn("set -euo pipefail", iso)
        self.assertIn('cmp "$(BUILD_DIR)/served-InRelease"', iso)
        self.assertIn("sudo lb build 2>&1 | tee", iso)
        self.assertNotIn("lb build ||", iso)
        self.assertGreaterEqual(iso.count("-nt $(LB_BUILD_MARKER)"), 2)
        self.assertIn("xargs -0 sha256sum > SHA256SUMS", iso)
        self.assertIn("sha256sum --check --quiet SHA256SUMS", iso)
        self.assertIn("sha256sum --check", iso)
        self.assertIn("--verify $(ROOT)/$(ISO_NAME).asc", makefile)
        self.assertIn("@$(MAKE) iso-gate", iso)
        self.assertIn("tools/iso_gate_2_1_4.py", makefile)
        self.assertIn("ISO_GATE_LOG", makefile)

    def test_first_boot_uses_utc_rtc_and_network_time(self):
        firstboot = (
            DEFAULTS / "data/usr/lib/shadowfetch/firstboot.sh"
        ).read_text()
        core_packages = (
            ROOT / "live-build/config/package-lists/shadowfetch-core.list.chroot"
        ).read_text().splitlines()
        self.assertIn(
            "timedatectl set-local-rtc 0 --adjust-system-clock", firstboot
        )
        self.assertNotIn("timedatectl set-local-rtc 1", firstboot)
        self.assertIn(
            "systemctl enable --now systemd-timesyncd.service", firstboot
        )
        self.assertIn("systemd-timesyncd", core_packages)

    def test_plymouth_has_visible_unlock_prompt_and_safe_status_rendering(self):
        script = PLYMOUTH.read_text()
        self.assertIn("UNLOCK ENCRYPTED DRIVE", script)
        self.assertIn("Enter your disk passphrase, then press Enter", script)
        self.assertIn("Plymouth.SetDisplayPasswordFunction", script)
        self.assertIn("Plymouth.SetDisplayNormalFunction", script)
        self.assertIn('Image("dot-gold.png").Scale', script)
        self.assertNotIn("Plymouth.GetTime", script)
        self.assertNotIn("Plymouth.SetUpdateStatusFunction", script)
        self.assertNotIn("Image.Text(text", script)

    def test_installed_ssh_is_reachable_through_the_default_firewall(self):
        firstboot = (
            DEFAULTS / "data/usr/lib/shadowfetch/firstboot.sh"
        ).read_text()
        postinst = (DEFAULTS / "debian/postinst").read_text()
        for script in (firstboot, postinst):
            self.assertIn("ufw limit OpenSSH", script)
            self.assertIn("ufw limit 22/tcp", script)
        self.assertIn('"$1" = "configure"', postinst)
        self.assertIn("ssh-keygen -A", postinst)
        self.assertIn("systemctl reset-failed ssh.service", postinst)
        self.assertIn("systemctl restart ssh.service", postinst)
        self.assertIn("/etc/ssh/ssh_host_ed25519_key", postinst)
        self.assertIn("/etc/ssh/ssh_host_rsa_key", postinst)

    def test_buzz_service_waits_for_explicit_setup_state(self):
        unit = (
            DEFAULTS / "data/usr/lib/systemd/user/shadowfetch-buzz.service"
        ).read_text()
        self.assertIn(
            "ConditionPathExists=%h/.local/share/shadowfetch/buzz/.env",
            unit,
        )

    def test_buzz_upstream_contract_is_locked(self):
        lock = json.loads((ROOT / "qa/2.1.4/upstream-buzz.json").read_text())
        self.assertEqual("desktop-v0.5.8", lock["tag"])
        self.assertRegex(lock["commit"], r"^[0-9a-f]{40}$")
        self.assertEqual("buzz", lock["debian_contract"]["package"])
        self.assertEqual("0.5.8", lock["debian_contract"]["version"])
        self.assertEqual("amd64", lock["debian_contract"]["architecture"])
        self.assertIn("mesh-llm", lock["release_build"]["linux_features"])
        self.assertEqual("0.2.1", lock["relay"]["tag"])
        self.assertRegex(lock["relay"]["commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(lock["relay"]["manifest_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(lock["relay"]["amd64_image_sha256"], r"^[0-9a-f]{64}$")
        for binary in ("/usr/bin/buzz", "/usr/bin/buzz-agent", "/usr/bin/buzz-desktop"):
            self.assertIn(binary, lock["debian_contract"]["required_binaries"])

    def test_nvidia_rtx_5080_contract_is_locked(self):
        lock = json.loads((ROOT / "qa/2.1.4/upstream-nvidia.json").read_text())
        self.assertTrue(lock["repository"]["signature_verified"])
        self.assertRegex(lock["repository"]["signing_fingerprint"], r"^[0-9A-F]{40}$")
        self.assertEqual("0x2C02", lock["rtx_5080"]["pci_device_id"])
        self.assertTrue(lock["rtx_5080"]["open_kernel_supported"])
        self.assertRegex(lock["keyring"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(
            lock["driver_assistant"]["supported_gpus_sha256"],
            r"^[0-9a-f]{64}$",
        )
        self.assertRegex(
            lock["release_time_packages"]["nvidia_open"]["version"],
            r"^610\.",
        )

    def test_legacy_nvidia_metapackage_installs_no_driver(self):
        control = (ROOT / "packages/shadowfetch-meta/debian/control").read_text()
        nvidia = control.split("Package: shadowfetch-nvidia", 1)[1]
        for package in (
            "nvidia-driver",
            "nvidia-settings",
            "nvidia-vaapi-driver",
            "libnvidia-encode1",
            "firmware-nvidia-gsp",
        ):
            self.assertNotRegex(nvidia, rf"(?m)^ {re.escape(package)},?$")
        self.assertIn("shadowfetch-defaults (= ${binary:Version})", nvidia)
        self.assertIn("Run shadowfetch-gpu", nvidia)

    def test_current_source_packages_target_umbra(self):
        package_names = (
            "shadowfetch-meta", "shadowfetch-welcome", "shadowfetch-themes",
            "shadowfetch-defaults", "shadowfetch-branding", "grub-btrfs",
            "shadowfetch-ember", "shadowfetch-firewatchd", "shadowfetch-phoenix",
            "shadowfetch-menus", "shadowfetch-control-center",
            "shadowfetch-fireproof", "shadowfetch-hwscan",
        )
        for package in package_names:
            first = (ROOT / "packages" / package / "debian/changelog").read_text().splitlines()[0]
            self.assertIn(") umbra; urgency=", first, package)

    def test_fireproof_uses_current_polkit_and_packaging_helpers(self):
        control = (ROOT / "packages/shadowfetch-fireproof/debian/control").read_text()
        postinst = (ROOT / "packages/shadowfetch-fireproof/debian/postinst").read_text()
        postrm = (ROOT / "packages/shadowfetch-fireproof/debian/postrm").read_text()
        self.assertNotIn("policykit-1", control)
        self.assertRegex(control, r"(?m)^ polkitd,$")
        self.assertRegex(control, r"(?m)^ pkexec,$")
        for script in (postinst, postrm):
            self.assertIn("deb-systemd-helper", script)
            self.assertNotRegex(script, r"(?m)^\s*systemctl\b")

    def test_buzz_relay_is_loopback_only_and_image_is_pinned(self):
        compose = BUZZ_COMPOSE.read_text()
        helper = BUZZ.read_text()
        lock = json.loads((ROOT / "qa/2.1.4/upstream-buzz.json").read_text())
        self.assertIn('"127.0.0.1:${BUZZ_HTTP_PORT:-3000}:3000"', compose)
        self.assertNotIn('"${BUZZ_HTTP_PORT:-3000}:3000"', compose)
        self.assertRegex(
            helper,
            r'BUZZ_IMAGE="ghcr\.io/block/buzz@sha256:[0-9a-f]{64}"',
        )
        self.assertIn(
            f'BUZZ_IMAGE="ghcr.io/block/buzz@sha256:{lock["relay"]["manifest_sha256"]}"',
            helper,
        )
        self.assertIn(
            'BUZZ_CORS_ORIGINS "tauri://localhost,http://tauri.localhost,'
            'http://127.0.0.1:3000"',
            helper,
        )
        self.assertRegex(
            helper,
            r'set_env_value "\$env_file" BUZZ_REQUIRE_AUTH_TOKEN false',
        )
        self.assertRegex(
            helper,
            r'set_env_value "\$env_file" BUZZ_REQUIRE_RELAY_MEMBERSHIP false',
        )
        self.assertIn('export BUZZ_RELAY_URL="$RELAY_URL"', helper)
        self.assertNotRegex(helper, r"(?m)^\s*(?:source|\.)\s+.*client\.env")

    def test_every_container_image_is_immutable(self):
        image_lines = [
            line.strip()
            for line in BUZZ_COMPOSE.read_text().splitlines()
            if line.strip().startswith("image:")
        ]
        self.assertEqual(5, len(image_lines))
        for line in image_lines:
            if "${BUZZ_IMAGE}" in line:
                continue
            self.assertRegex(line, r"@sha256:[0-9a-f]{64}$")

    def test_buzz_package_is_checksum_and_transaction_gated(self):
        provision = PROVISION.read_text()
        lock = json.loads((ROOT / "qa/2.1.4/upstream-buzz.json").read_text())
        digest = lock["asset"]["sha256"]
        self.assertIn(f'BUZZ_DEB_SHA256="{digest}"', provision)
        self.assertIn("--proto '=https'", provision)
        self.assertIn("dpkg --audit", provision)
        self.assertIn("dpkg --compare-versions", provision)
        verify_at = provision.index("sha256sum --check --status")
        simulate_at = provision.index('-s install "$deb"')
        apply_at = provision.index('--no-remove install -y "$deb"')
        self.assertLess(verify_at, simulate_at)
        self.assertLess(simulate_at, apply_at)
        self.assertIn("grep -q '^Remv '", provision)
        self.assertIn("trap cleanup EXIT", provision)
        self.assertIn("trap - EXIT", provision)
        self.assertNotRegex(provision, r"trap\s+['\"]")
        self.assertNotRegex(provision, r"curl[^\n|]*\|\s*(?:ba)?sh\b")

    def test_live_user_cleanup_requires_a_nonempty_account_name(self):
        cleanup = (
            ROOT
            / "live-build/config/includes.chroot/usr/local/sbin/"
            "sf-remove-live-user"
        ).read_text()
        self.assertIn("LIVE_USER=shadow", cleanup)
        self.assertIn('rm -rf -- "/home/${LIVE_USER:?}"', cleanup)
        self.assertNotIn('rm -rf "/home/$USER"', cleanup)
        self.assertIn('grep -q "^${LIVE_USER}:" /etc/shadow', cleanup)

    def test_installed_manifest_has_buzz_and_no_retired_launchers(self):
        manifest = (DEFAULTS / "debian/shadowfetch-defaults.install").read_text()
        for expected in (
            "data/usr/bin/shadowfetch-buzz",
            "data/usr/libexec/shadowfetch-buzz-bootstrap",
            "data/usr/libexec/shadowfetch-buzz-provision",
            "data/usr/libexec/shadowfetch-buzz-stack",
            "data/usr/libexec/shadowfetch-migrate-2.1.3-ai",
            "data/usr/share/shadowfetch/buzz/compose.yml",
            "data/usr/lib/systemd/user/shadowfetch-buzz.service",
            "data/usr/lib/systemd/system/shadowfetch-migrate-2.1.3-ai.service",
            "data/usr/share/shadowfetch/migrations/2.1.3-ai-packages",
            "data/usr/share/doc/shadowfetch/BUZZ.md",
        ):
            self.assertIn(expected, manifest)
        self.assertNotRegex(
            manifest,
            re.compile(r"openclaw|hermes|shadowfetch-(?:assistant|llm|ai)(?:\s|\.)", re.I),
        )
        self.assertNotIn("80shadowfetch-snapshot", manifest)
        self.assertNotIn("apt-snapshot.sh", manifest)
        self.assertFalse(
            (DEFAULTS / "data/etc/apt/apt.conf.d/80shadowfetch-snapshot").exists()
        )
        self.assertFalse(
            (DEFAULTS / "data/usr/lib/shadowfetch/apt-snapshot.sh").exists()
        )

    def test_runtime_dependencies_cover_first_run_preflight(self):
        control = (DEFAULTS / "debian/control").read_text()
        depends = control.split("Depends:", 1)[1].split("Recommends:", 1)[0]
        for package in (
            "curl",
            "iproute2",
            "konsole",
            "libnotify-bin",
            "pciutils",
            "pkexec",
            "polkitd",
            "podman",
            "podman-compose",
            "psmisc",
            "sudo",
            "vulkan-tools",
            "wl-clipboard",
            "xclip",
            "xdg-utils",
        ):
            self.assertRegex(depends, rf"(?m)^ {re.escape(package)},?$", package)
        self.assertNotRegex(depends, r"(?m)^ zstd,?$")

    def test_vendor_units_and_udev_rules_use_vendor_paths(self):
        manifest = (DEFAULTS / "debian/shadowfetch-defaults.install").read_text()
        for name in (
            "flatpak-system-update.service",
            "flatpak-system-update.timer",
            "rfkill-unblock.service",
            "shadowfetch-regdomain.service",
        ):
            self.assertIn(f"data/usr/lib/systemd/system/{name}", manifest)
            self.assertFalse((DEFAULTS / "data/etc/systemd/system" / name).exists())
        rule = "60-shadowfetch-ioschedulers.rules"
        self.assertIn(f"data/usr/lib/udev/rules.d/{rule}", manifest)
        self.assertFalse((DEFAULTS / "data/etc/udev/rules.d" / rule).exists())
        maintscript = (DEFAULTS / "debian/shadowfetch-defaults.maintscript").read_text()
        for old_path in (
            "/etc/systemd/system/flatpak-system-update.service",
            "/etc/systemd/system/flatpak-system-update.timer",
            "/etc/systemd/system/rfkill-unblock.service",
            "/etc/systemd/system/shadowfetch-regdomain.service",
            "/etc/udev/rules.d/60-shadowfetch-ioschedulers.rules",
            "/etc/apt/apt.conf.d/80shadowfetch-snapshot",
            "/etc/systemd/system/ollama.service.d/10-localhost.conf",
        ):
            self.assertIn(f"rm_conffile {old_path} 2.1.4-1~", maintscript)

    def test_pre_2_1_4_postinst_marks_retirement_without_deleting_user_data(self):
        postinst = (DEFAULTS / "debian/postinst").read_text()
        self.assertIn('dpkg --compare-versions "$2" lt \'2.1.4~\'', postinst)
        self.assertIn("2.1.3-ai.pending", postinst)
        self.assertIn("systemctl disable --now llama-server.service", postinst)
        self.assertIn(
            "a458253d5a6b22fbb3c73677ba88d7d87307da985b85ba6d1935dec5f51ffc92",
            postinst,
        )
        self.assertNotRegex(postinst, r"rm\s+-rf\s+/(?:home|var/lib)")

    def test_retired_package_helper_has_an_exact_no_data_deletion_contract(self):
        helper = MIGRATION_HELPER.read_text()
        unit = (
            DEFAULTS
            / "data/usr/lib/systemd/system/shadowfetch-migrate-2.1.3-ai.service"
        ).read_text()
        self.assertIn(
            "6eeddfe229f65e64288c34b88e23ad19a859de31688d73d29817244f064d6dd5",
            helper,
        )
        self.assertIn("apt-get -s", helper)
        self.assertIn('cmp -s "$temporary/expected" "$temporary/planned"', helper)
        self.assertIn('remove "${installed[@]}"', helper)
        self.assertNotIn("purge", helper)
        self.assertNotRegex(helper, r"rm\s+-rf\s+/(?:home|var/lib)")
        self.assertIn("ConditionPathExists=", unit)
        self.assertIn("ExecCondition=", unit)
        self.assertIn("SuccessExitStatus=75", unit)

    def test_systemd_units_do_not_use_invalid_directive_names(self):
        invalid = ("ConditionPathIsExecutable=", "ProtectClocks=")
        findings = []
        for path in (ROOT / "packages").glob("shadowfetch-*/data/**/*.service"):
            content = path.read_text()
            for directive in invalid:
                if directive in content:
                    findings.append(f"{path.relative_to(ROOT)}: {directive}")
        self.assertEqual([], findings)

    def test_packaged_launchers_have_one_owner_and_one_main_category(self):
        main_categories = {
            "AudioVideo", "Audio", "Video", "Development", "Education",
            "Game", "Graphics", "Network", "Office", "Science", "Settings",
            "System", "Utility",
        }
        owners = {}
        installed_sources = set()
        for package in (ROOT / "packages").iterdir():
            if not package.is_dir():
                continue
            for manifest in (package / "debian").glob("*.install"):
                for raw_line in manifest.read_text().splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    fields = line.split()
                    if len(fields) < 2 or "usr/share/applications" not in fields[-1]:
                        continue
                    source = package / fields[0]
                    self.assertTrue(source.is_file(), source)
                    target = f"usr/share/applications/{source.name}"
                    self.assertNotIn(
                        target,
                        owners,
                        f"{target}: {owners.get(target)} and {source}",
                    )
                    owners[target] = source
                    installed_sources.add(source.resolve())
                    content = source.read_text()
                    match = re.search(r"(?m)^Categories=([^\n]+)$", content)
                    self.assertIsNotNone(match, source)
                    categories = {value for value in match.group(1).split(";") if value}
                    selected = categories & main_categories
                    self.assertEqual(1, len(selected), f"{source}: {sorted(selected)}")
            for source_root in (
                package / "data/usr/share/applications",
                package / "usr/share/applications",
            ):
                if source_root.is_dir():
                    for source in source_root.glob("*.desktop"):
                        self.assertIn(
                            source.resolve(),
                            installed_sources,
                            f"unused launcher: {source}",
                        )
        self.assertIn("usr/share/applications/shadowfetch-local-ai.desktop", owners)
        self.assertIn("usr/share/applications/shadowfetch-buzz.desktop", owners)

    def test_local_ai_launchers_have_one_predictable_menu(self):
        menu = (
            ROOT
            / "packages/shadowfetch-menus/etc/xdg/menus/applications-merged/"
            "shadowfetch-launcher.menu"
        ).read_text()
        self.assertGreaterEqual(
            menu.count("<Not><Category>X-Shadowfetch-AI</Category></Not>"),
            2,
        )
        self.assertIn("<Filename>shadowfetch-local-ai.desktop</Filename>", menu)
        self.assertIn("<Directory>shadowfetch-local-ai.directory</Directory>", menu)
        self.assertNotIn("shadowfetch-ai.directory", menu)

    def test_welcome_catalog_has_no_model_download_records(self):
        catalog = (
            ROOT
            / "packages/shadowfetch-welcome/data/usr/share/shadowfetch/welcome/catalog"
        )
        records = [json.loads(path.read_text()) for path in catalog.glob("*.json")]
        self.assertTrue(records)
        self.assertNotIn("model", {record["kind"] for record in records})
        self.assertEqual([], list(catalog.glob("model-*.json")))
        readme = (catalog / "README").read_text()
        self.assertIn("Buzz's native Compute workflow", readme)
        self.assertNotIn("shadowfetch-ai", readme)

    def test_buzz_is_the_only_model_owner_in_current_guidance(self):
        welcome = WELCOME.read_text()
        guide = (DEFAULTS / "data/usr/share/doc/shadowfetch/BUZZ.md").read_text()
        release = (ROOT / "docs/RELEASE-2.1.4.md").read_text()
        for content in (welcome, guide, release, BUZZ.read_text()):
            self.assertIn("Buzz", content)
            self.assertNotRegex(
                content,
                re.compile(r"\bollama\b|ministral|open[- ]?webui", re.I),
            )
        self.assertIn("Settings > Compute", guide)
        self.assertIn("Settings > Compute", BUZZ.read_text())
        self.assertNotIn("--model", BUZZ.read_text())

    def test_shipped_programs_and_build_hooks_are_executable(self):
        paths = (
            BUZZ,
            PROVISION,
            BUZZ_STACK,
            MIGRATION_HELPER,
            DEFAULTS / "data/usr/bin/shadowfetch-gpu",
            DEFAULTS / "data/usr/bin/shadowfetch-update",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-workspace",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-doctor",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-tools",
            ROOT / "live-build/config/hooks/0020-gpu-firstboot.hook.chroot",
            WELCOME,
        )
        for path in paths:
            self.assertTrue(os.access(path, os.X_OK), path)

    def test_shell_and_python_entrypoints_parse(self):
        shell_files = [
            BUZZ,
            PROVISION,
            BUZZ_STACK,
            MIGRATION_HELPER,
            DEFAULTS / "data/usr/bin/shadowfetch-gpu",
            DEFAULTS / "data/usr/bin/shadowfetch-update",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-doctor",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-tools",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-workspace",
        ]
        for path in shell_files:
            result = subprocess.run(
                ["bash", "-n", str(path)], capture_output=True, text=True
            )
            self.assertEqual(0, result.returncode, result.stderr)
        python_files = (
            WELCOME,
            DEFAULTS / "data/usr/bin/shadowfetch-health",
            DEFAULTS / "data/usr/bin/shadowfetch-facts",
            CONTROL / "usr/share/shadowfetch/control-center/sfcc/agents_page.py",
            CONTROL / "usr/share/shadowfetch/control-center/sfcc/firewatch_page.py",
        )
        with tempfile.TemporaryDirectory() as temporary:
            for index, path in enumerate(python_files):
                py_compile.compile(
                    str(path),
                    cfile=str(Path(temporary) / f"{index}.pyc"),
                    doraise=True,
                )

    def test_welcome_stylesheet_parses_in_offscreen_qt(self):
        script = textwrap.dedent(
            f"""
            import importlib.machinery
            import importlib.util
            from pathlib import Path

            path = Path({str(WELCOME)!r})
            loader = importlib.machinery.SourceFileLoader("sf_welcome_qa", str(path))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
            app = module.QApplication([])
            window = module.ShadowfetchWelcome(mode="catalog")
            window.show()
            app.processEvents()
            window.close()
            """
        )
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        with tempfile.TemporaryDirectory() as home:
            env["HOME"] = home
            result = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                env=env,
                timeout=20,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("Could not parse stylesheet", result.stderr)

    def test_help_paths_are_read_only(self):
        paths = (
            BUZZ,
            PROVISION,
            DEFAULTS / "data/usr/bin/shadowfetch-gpu",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-workspace",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-doctor",
            DEFAULTS / "data/usr/bin/shadowfetch-agent-tools",
        )
        for path in paths:
            result = subprocess.run(
                ["bash", str(path), "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(0, result.returncode, f"{path}: {result.stderr}")
            self.assertIn("USAGE", result.stdout, path)

    def test_buzz_service_uses_ordered_readiness_helper(self):
        unit = (
            DEFAULTS / "data/usr/lib/systemd/user/shadowfetch-buzz.service"
        ).read_text()
        helper = BUZZ_STACK.read_text()
        compose = BUZZ_COMPOSE.read_text()
        self.assertIn("ExecStart=/usr/libexec/shadowfetch-buzz-stack start", unit)
        self.assertIn("/_readiness", helper)
        self.assertIn('run --rm minio-init', helper)
        self.assertIn("TimeoutStartSec=1800", unit)
        self.assertIn("restart shadowfetch-buzz.service", BUZZ.read_text())
        relay = compose.split("  relay:", 1)[1].split("  postgres:", 1)[0]
        self.assertNotIn("minio-init", relay)

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux lock test")
    def test_buzz_stack_lock_is_not_inherited_by_service_children(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "bin"
            fake.mkdir()
            child_pid = root / "child.pid"
            self._write_executable(
                fake / "podman-compose",
                f"""
                sleep 5 >/dev/null 2>&1 &
                printf '%s\\n' "$!" > {child_pid!s}
                """,
            )
            (root / "compose.yml").write_text("services: {}\n")
            env_file = root / ".env"
            env_file.write_text("BUZZ_HTTP_PORT=3000\n")
            env_file.chmod(0o600)
            env = os.environ.copy()
            env.update({
                "HOME": str(root / "home"),
                "XDG_RUNTIME_DIR": str(root / "run"),
                "PATH": f"{fake}:/usr/bin:/bin",
                "SHADOWFETCH_BUZZ_PROJECT": "qa-lock",
                "SHADOWFETCH_BUZZ_COMPOSE_FILE": "compose.yml",
                "SHADOWFETCH_BUZZ_ENV_FILE": ".env",
            })
            (root / "home").mkdir()
            try:
                first = subprocess.run(
                    [str(BUZZ_STACK), "stop"],
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                second = subprocess.run(
                    [str(BUZZ_STACK), "stop"],
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(0, first.returncode, first.stderr)
                self.assertEqual(0, second.returncode, second.stderr)
            finally:
                if child_pid.exists():
                    os.kill(int(child_pid.read_text().strip()), 9)

    def test_welcome_uses_one_buzz_native_choice(self):
        welcome = WELCOME.read_text()
        buzz_page = welcome.split("class BuzzPage", 1)[1].split(
            "class InstallPage", 1
        )[0]
        self.assertIn('("install-buzz", "Install Buzz"', buzz_page)
        self.assertIn('("none", "Not now"', buzz_page)
        self.assertNotIn("QComboBox", welcome)
        self.assertNotIn("Buzz plus model", welcome)
        self.assertIn("ranks open-source models", buzz_page)

    def test_first_run_completion_waits_for_buzz_or_explicit_skip(self):
        welcome = WELCOME.read_text()
        install = welcome.split("class InstallPage", 1)[1].split(
            "class ShadowfetchWelcome", 1
        )[0]
        self.assertIn('[helper, "setup", "--yes", "--no-open"]', install)
        self.assertIn('self.buzz_state = "ready"', install)
        finish = install.split("    def _finish(self):", 1)[1].split(
            "    def _skip_buzz", 1
        )[0]
        self.assertLess(
            finish.index('if self.buzz_state == "failed"'),
            finish.index("WELCOME_DONE_FLAG.touch()"),
        )
        self.assertLess(
            finish.index("if self.busy"),
            finish.index("WELCOME_DONE_FLAG.touch()"),
        )
        skip = install.split("    def _skip_buzz", 1)[1]
        self.assertIn("WELCOME_DONE_FLAG.touch()", skip)

    def test_welcome_cancellation_escalates_without_blocking_the_ui(self):
        welcome = WELCOME.read_text()
        command_worker = welcome.split("class CommandWorker", 1)[1].split(
            "class StreamingCommandWorker", 1
        )[0]
        worker = welcome.split("class StreamingCommandWorker", 1)[1].split(
            "class Card", 1
        )[0]
        for content in (command_worker, worker):
            for expected in (
                "start_new_session=True",
                "threading.Thread",
                "os.killpg",
                "signal.SIGINT",
                "signal.SIGTERM",
                "signal.SIGKILL",
            ):
                self.assertIn(expected, content)
        self.assertNotIn("subprocess.run", command_worker)
        self.assertIn('for name in ("buzz_worker", "worker")', welcome)
        self.assertIn("worker.cancel()", welcome)
        self.assertIn("Setup is still running", welcome)
        self.assertIn("Cancel setup", welcome)
        self.assertIn("Retry Buzz", welcome)

    def test_user_workspace_helpers_reject_unsafe_invocation(self):
        workspace = (DEFAULTS / "data/usr/bin/shadowfetch-agent-workspace").read_text()
        doctor = (DEFAULTS / "data/usr/bin/shadowfetch-agent-doctor").read_text()
        tools = (DEFAULTS / "data/usr/bin/shadowfetch-agent-tools").read_text()
        self.assertIn("EUID != 0", workspace)
        self.assertIn('[[ "$ROOT" != / ]]', workspace)
        self.assertIn("realpath -m", workspace)
        self.assertGreaterEqual(workspace.count('"$safe" != ..'), 2)
        self.assertIn('"$name" != ..', workspace)
        for content in (doctor, tools):
            self.assertIn('Unknown option: $1', content)

    def test_buzz_service_start_failure_prints_diagnostics(self):
        buzz = BUZZ.read_text()
        start = buzz.split("start_relay()", 1)[1].split("cmd_setup()", 1)[0]
        self.assertIn("ensure_user_service_bus", start)
        self.assertIn("if ! systemctl --user restart", start)
        self.assertIn("systemctl --user --no-pager status", start)
        self.assertIn("journalctl --user -u shadowfetch-buzz.service", start)

    def test_buzz_setup_recovers_the_desktop_user_bus_for_terminal_launches(self):
        buzz = BUZZ.read_text()
        helper = buzz.split("ensure_user_service_bus()", 1)[1].split(
            "relay_ready()", 1
        )[0]
        self.assertIn('runtime_dir="/run/user/$(id -u)"', helper)
        self.assertIn("export XDG_RUNTIME_DIR", helper)
        self.assertIn("DBUS_SESSION_BUS_ADDRESS", helper)
        self.assertIn('unix:path=${XDG_RUNTIME_DIR}/bus', helper)

    def test_buzz_first_owner_bootstrap_is_scoped_and_secret_free(self):
        bootstrap = BUZZ_BOOTSTRAP.read_text()
        launcher = BUZZ.read_text()
        self.assertIn("c.host='$COMMUNITY_HOST' AND e.kind=9007", bootstrap)
        self.assertIn("((${#candidates[@]} != 1))", bootstrap)
        self.assertIn("buzz-admin add-member", bootstrap)
        self.assertIn('--pubkey "$candidate" --role admin', bootstrap)
        self.assertIn("if ((member_count > 0))", bootstrap)
        self.assertIn("com.docker.compose.project=$PROJECT", bootstrap)
        self.assertIn("com.docker.compose.service=$service", bootstrap)
        self.assertRegex(bootstrap, r"\^127\\\.0\\\.0\\\.1:")
        self.assertNotRegex(
            bootstrap,
            re.compile(r"private[_ -]?key|generate-key|\bnsec\b", re.I),
        )
        self.assertIn("prepare_first_owner", launcher)
        self.assertIn('printf \'%s\' "$RELAY_URL"', launcher)
        self.assertIn('"$OWNER_BOOTSTRAP"', launcher)

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux bootstrap test")
    def test_buzz_first_owner_bootstrap_enrols_one_candidate_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "bin"
            fake.mkdir()
            member = root / "member"
            call = root / "add-member-call"
            self._write_executable(
                fake / "podman",
                """
                command=$1
                shift
                case "$command" in
                    ps)
                        case " $* " in
                            *"service=relay"*) printf 'qa-relay\\n' ;;
                            *"service=postgres"*) printf 'qa-postgres\\n' ;;
                        esac
                        ;;
                    exec)
                        if [ "${1:-}" = "-u" ]; then shift 2; fi
                        container=$1
                        shift
                        case "${1:-}" in
                            psql)
                                case " $* " in
                                    *"SELECT count(*)"*)
                                        if [ -e "$TEST_MEMBER_FILE" ]; then
                                            printf '1\\n'
                                        else
                                            printf '0\\n'
                                        fi
                                        ;;
                                    *"e.kind=9007"*) printf '%s\\n' "$TEST_CANDIDATES" ;;
                                esac
                                ;;
                            buzz-admin)
                                shift
                                printf '%s\\n' "$*" > "$TEST_CALL_FILE"
                                touch "$TEST_MEMBER_FILE"
                                ;;
                        esac
                        ;;
                esac
                """,
            )
            state = root / "state"
            candidate = "ab" * 32
            env = os.environ.copy()
            env.update({
                "HOME": str(root / "home"),
                "PATH": f"{fake}:/usr/bin:/bin",
                "SHADOWFETCH_BUZZ_STATE_DIR": str(state),
                "SHADOWFETCH_BUZZ_BOOTSTRAP_ATTEMPTS": "1",
                "SHADOWFETCH_BUZZ_BOOTSTRAP_INTERVAL": "0",
                "TEST_MEMBER_FILE": str(member),
                "TEST_CALL_FILE": str(call),
                "TEST_CANDIDATES": candidate,
            })
            (root / "home").mkdir()
            result = subprocess.run(
                [str(BUZZ_BOOTSTRAP)],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                f"add-member --pubkey {candidate} --role admin",
                call.read_text().strip(),
            )
            self.assertTrue((state / "local-owner-enrolled").is_file())

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux bootstrap test")
    def test_buzz_first_owner_bootstrap_refuses_ambiguous_candidates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "bin"
            fake.mkdir()
            member = root / "member"
            call = root / "add-member-call"
            self._write_executable(
                fake / "podman",
                """
                command=$1
                shift
                case "$command" in
                    ps)
                        case " $* " in
                            *"service=relay"*) printf 'qa-relay\\n' ;;
                            *"service=postgres"*) printf 'qa-postgres\\n' ;;
                        esac
                        ;;
                    exec)
                        if [ "${1:-}" = "-u" ]; then shift 2; fi
                        shift
                        case "${1:-}" in
                            psql)
                                case " $* " in
                                    *"SELECT count(*)"*) printf '0\\n' ;;
                                    *"e.kind=9007"*) printf '%s\\n' "$TEST_CANDIDATES" ;;
                                esac
                                ;;
                            buzz-admin) touch "$TEST_CALL_FILE" ;;
                        esac
                        ;;
                esac
                """,
            )
            state = root / "state"
            env = os.environ.copy()
            env.update({
                "HOME": str(root / "home"),
                "PATH": f"{fake}:/usr/bin:/bin",
                "SHADOWFETCH_BUZZ_STATE_DIR": str(state),
                "SHADOWFETCH_BUZZ_BOOTSTRAP_ATTEMPTS": "1",
                "SHADOWFETCH_BUZZ_BOOTSTRAP_INTERVAL": "0",
                "TEST_MEMBER_FILE": str(member),
                "TEST_CALL_FILE": str(call),
                "TEST_CANDIDATES": f"{'ab' * 32}\n{'cd' * 32}",
            })
            (root / "home").mkdir()
            result = subprocess.run(
                [str(BUZZ_BOOTSTRAP)],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(4, result.returncode)
            self.assertIn("multiple first-owner candidates", result.stderr)
            self.assertFalse(call.exists())
            self.assertFalse((state / "local-owner-enrolled").exists())

    def test_no_shipped_helper_uses_an_unverified_pipe_installer(self):
        for directory in (DEFAULTS / "data/usr/bin", DEFAULTS / "data/usr/libexec"):
            for path in directory.iterdir():
                if not path.is_file():
                    continue
                try:
                    content = path.read_text()
                except UnicodeDecodeError:
                    continue
                self.assertNotRegex(
                    content, r"curl[^\n|]*\|\s*(?:ba)?sh\b", path
                )

    def test_graphics_claims_require_measured_hardware_renderer(self):
        welcome = WELCOME.read_text()
        gpu = (DEFAULTS / "data/usr/bin/shadowfetch-gpu").read_text()
        hook = (
            ROOT / "live-build/config/hooks/0020-gpu-firstboot.hook.chroot"
        ).read_text()
        self.assertNotIn("already give you full acceleration", welcome)
        for content in (welcome, gpu, hook):
            self.assertRegex(content, r"llvmpipe.*lavapipe")
            self.assertIn("vulkaninfo", content)
        self.assertIn("No DRM render node", gpu)
        self.assertIn("/dev/dri/renderD*", gpu)
        self.assertIn("--distro debian:13", gpu)
        self.assertIn("apt_install_no_remove", gpu)
        self.assertIn("-s install", gpu)
        self.assertIn("--no-remove install -y", gpu)
        self.assertIn("grep -q '^Remv '", gpu)
        self.assertNotIn("nvidia-driver-assistant --install", gpu)
        self.assertRegex(
            gpu,
            r"recommended.*\^\(nvidia-open\|cuda-drivers\)",
        )

    def test_update_simulates_twice_and_refuses_unverified_removals(self):
        update = (DEFAULTS / "data/usr/bin/shadowfetch-update").read_text()
        self.assertIn("apt-get -s", update)
        self.assertIn("/^Remv /", update)
        self.assertIn("validate_removals", update)
        self.assertIn("plan_fingerprint", update)
        self.assertIn("will not apply unverified package removals", update)
        self.assertIn("libprocesscore10", update)
        self.assertIn("libprocesscore11", update)
        self.assertIn("qml6-module-org-kde-milou", update)
        self.assertIn("transaction=(--no-remove full-upgrade)", update)
        self.assertIn("flock -n", update)
        self.assertIn("80snapper", update)
        self.assertIn("write_snapper_rows", update)
        self.assertIn("snapper_first_pre_after", update)
        self.assertRegex(
            update,
            re.compile(r"load_migration_plan\(\).*?\n    return 0\n}", re.S),
        )
        self.assertNotRegex(update, r"\$\([^)]*snapper_rows")
        self.assertNotRegex(update, r"snapper[^\n]*create")
        self.assertIn("trap cleanup EXIT", update)
        self.assertNotRegex(update, r"trap\s+['\"]")

    def test_branding_refreshes_os_release_after_package_updates(self):
        branding = ROOT / "packages/shadowfetch-branding/debian"
        postinst = (branding / "postinst").read_text()
        triggers = (branding / "triggers").read_text()
        self.assertIn("configure|triggered", postinst)
        self.assertIn("/usr/share/shadowfetch/os-release.shadowfetch", postinst)
        self.assertIn("VERSION_ID=\\\"$version\\\"", postinst)
        self.assertIn("install -m 0644 \"$source\" /usr/lib/os-release", postinst)
        self.assertEqual("interest-noawait /usr/lib/os-release\n", triggers)

    def test_health_checks_buzz_native_ports_only(self):
        health = (DEFAULTS / "data/usr/bin/shadowfetch-health").read_text()
        doctor = (DEFAULTS / "data/usr/bin/shadowfetch-agent-doctor").read_text()
        for content in (health, doctor):
            self.assertIn("9337", content)
            self.assertIn("3000", content)
            self.assertNotIn("11434", content)
            self.assertNotRegex(content, re.compile(r"\bollama\b", re.I))

    @staticmethod
    def _write_executable(path: Path, body: str) -> None:
        path.write_text("#!/bin/sh\nset -eu\n" + textwrap.dedent(body))
        path.chmod(0o755)

    def _buzz_failure_env(self, root: Path, listener_port=None, free=100000):
        fake = root / "bin"
        fake.mkdir()
        marker = root / "provision-called"
        compose = root / "compose.yml"
        compose.write_text("services: {}\n")
        self._write_executable(fake / "podman", "exit 0\n")
        self._write_executable(fake / "podman-compose", "exit 0\n")
        if listener_port is None:
            self._write_executable(fake / "ss", "exit 0\n")
        else:
            self._write_executable(
                fake / "ss",
                f"printf 'LISTEN 0 128 127.0.0.1:{listener_port} 0.0.0.0:*\\n'\n",
            )
        self._write_executable(fake / "curl", "exit 22\n")
        self._write_executable(
            fake / "df",
            f"""
            printf 'Filesystem 1-blocks Used Available Capacity Mounted on\\n'
            printf 'fake 100000000 99900000 {free} 99%% /\\n'
            """,
        )
        self._write_executable(fake / "pkexec", f"touch {marker!s}\nexit 1\n")
        home = root / "home"
        home.mkdir()
        env = os.environ.copy()
        env.update({
            "DISPLAY": ":1",
            "HOME": str(home),
            "XDG_RUNTIME_DIR": str(root / "run"),
            "PATH": f"{fake}:/usr/bin:/bin",
            "SHADOWFETCH_BUZZ_COMPOSE_SOURCE": str(compose),
        })
        return env, marker

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux failure-injection test")
    def test_low_disk_fails_before_buzz_provisioning(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            env, marker = self._buzz_failure_env(root, free=100000)
            result = subprocess.run(
                [str(BUZZ), "setup", "--yes", "--no-open"],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("at least 8 GiB", result.stderr)
            self.assertFalse(marker.exists(), "provisioning ran before the disk gate")

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux setup-flow test")
    def test_successful_buzz_no_open_setup_returns_zero(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            env, _ = self._buzz_failure_env(root, free=100000000000)
            fake = root / "bin"
            self._write_executable(fake / "curl", "exit 0\n")
            self._write_executable(fake / "pkexec", "exit 0\n")
            self._write_executable(fake / "systemctl", "exit 0\n")
            result = subprocess.run(
                [str(BUZZ), "setup", "--yes", "--no-open"],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("passed setup checks", result.stdout)

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux failure-injection test")
    def test_occupied_buzz_ports_fail_before_provisioning(self):
        for port in (3000, 9337):
            with self.subTest(port=port), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                env, marker = self._buzz_failure_env(
                    root, listener_port=port, free=100000000000
                )
                result = subprocess.run(
                    [str(BUZZ), "setup", "--yes", "--no-open"],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn(f"Port {port}", result.stderr)
                self.assertFalse(marker.exists(), f"provisioning ran with port {port} occupied")

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux failure-injection test")
    def test_invalid_buzz_stack_port_fails_before_podman(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "bin"
            fake.mkdir()
            marker = root / "podman-called"
            self._write_executable(fake / "podman", f"touch {marker!s}\nexit 1\n")
            self._write_executable(
                fake / "podman-compose", f"touch {marker!s}\nexit 1\n"
            )
            (root / "compose.yml").write_text("services: {}\n")
            env_file = root / ".env"
            env_file.write_text("BUZZ_HTTP_PORT=80\n")
            env_file.chmod(0o600)
            env = os.environ.copy()
            env.update({
                "HOME": str(root / "home"),
                "XDG_RUNTIME_DIR": str(root / "run"),
                "PATH": f"{fake}:/usr/bin:/bin",
                "SHADOWFETCH_BUZZ_PROJECT": "qa-invalid-port",
                "SHADOWFETCH_BUZZ_COMPOSE_FILE": "compose.yml",
                "SHADOWFETCH_BUZZ_ENV_FILE": ".env",
            })
            (root / "home").mkdir()
            result = subprocess.run(
                [str(BUZZ_STACK), "start"],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("1024 through 65535", result.stderr)
            self.assertFalse(marker.exists(), "Podman ran with an invalid port")

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux failure-injection test")
    def test_update_rejects_solver_removal_before_apply(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "bin"
            fake.mkdir()
            marker = root / "upgrade-applied"
            self._write_executable(
                fake / "df",
                """
                printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\\n'
                printf 'fake 1 1 99999999 1%% /\\n'
                """,
            )
            self._write_executable(fake / "curl", "exit 0\n")
            self._write_executable(fake / "upower", "exit 0\n")
            self._write_executable(fake / "fuser", "exit 1\n")
            self._write_executable(fake / "dpkg", "exit 0\n")
            self._write_executable(fake / "apt", "exit 0\n")
            self._write_executable(fake / "sudo", 'exec "$@"\n')
            self._write_executable(
                fake / "apt-get",
                f"""
                case " $* " in
                    *" -s "*) printf 'Remv protected-package [1.0]\\n' ;;
                    *" full-upgrade "*) touch {marker!s} ;;
                esac
                """,
            )
            env = os.environ.copy()
            env.update({
                "HOME": str(root / "home"),
                "XDG_STATE_HOME": str(root / "state"),
                "PATH": f"{fake}:/usr/bin:/bin",
            })
            (root / "home").mkdir()
            result = subprocess.run(
                [str(DEFAULTS / "data/usr/bin/shadowfetch-update"), "--check"],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Unverified proposed removals", result.stdout)
            self.assertIn("protected-package", result.stdout)
            self.assertFalse(marker.exists(), "upgrade ran despite the removal plan")

    @unittest.skipUnless(Path("/usr/bin/flock").exists(), "Linux transition test")
    def test_update_accepts_only_a_verified_debian_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "bin"
            fake.mkdir()
            marker = root / "upgrade-applied"
            self._write_executable(
                fake / "df",
                """
                printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\n'
                printf 'fake 1 1 99999999 1%% /\n'
                """,
            )
            self._write_executable(fake / "curl", "exit 0\n")
            self._write_executable(fake / "upower", "exit 0\n")
            self._write_executable(fake / "fuser", "exit 1\n")
            self._write_executable(fake / "dpkg", "exit 0\n")
            self._write_executable(fake / "apt", "exit 0\n")
            self._write_executable(fake / "sudo", 'exec "$@"\n')
            self._write_executable(
                fake / "apt-get",
                f"""
                case " $* " in
                    *" -s "*)
                        printf 'Remv milou [4:6.6.5-2]\\n'
                        printf 'Inst qml6-module-org-kde-milou (4:6.7.2-2)\\n'
                        ;;
                    *" full-upgrade "*) touch {marker!s} ;;
                esac
                """,
            )
            env = os.environ.copy()
            env.update({
                "HOME": str(root / "home"),
                "XDG_STATE_HOME": str(root / "state"),
                "PATH": f"{fake}:/usr/bin:/bin",
            })
            (root / "home").mkdir()
            result = subprocess.run(
                [str(DEFAULTS / "data/usr/bin/shadowfetch-update"), "--check"],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Verified replacement or retirement removals", result.stdout)
            self.assertIn("milou", result.stdout)
            self.assertFalse(marker.exists(), "check mode applied the upgrade")


if __name__ == "__main__":
    unittest.main()
