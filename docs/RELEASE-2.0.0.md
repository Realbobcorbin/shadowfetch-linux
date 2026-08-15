# Shadowfetch Linux 2.0.0 "Umbra" — Bedrock

Released 2026-07-21. Major release. Codename **Umbra** (unchanged; it is the
visual-identity and APT-suite name). The 2.0 line is **Bedrock**: an unbreakable
foundation via boot-to-snapshot rollback, a graceful on-device AI assistant, a
crisp visual refresh, deeper hardening, and full license/source compliance.

## Identity
- ISO: shadowfetch-2.0.0-amd64.iso
- SHA-256: 0cbf9b90a4e561c57167cbac55d6fc4d02efc3dbd12a9c97c5034afc9fe6c671
- Signing key: 8F13 CE15 35EE 1F4A 2916 A1F7 3C5C 900B 7BE8 0CA1
- Base: Debian testing, KDE Plasma 6 (Wayland), Calamares installer
- Hybrid BIOS + UEFI; amd64
- squashfs 4042.75 MiB (under the 4 GiB ISO-9660 per-file limit)

## Headline changes
1. Boot-to-snapshot ("Bedrock"). grub-btrfs (vendored v4.14 — removed from
   Debian) plus a btrfs @snapshots subvolume plus an automatic pre-apt snapshot
   hook. Every apt transaction takes a snapshot; a broken upgrade is one reboot
   away from a known-good system, chosen from the GRUB menu. snapper timers and
   grub-btrfsd enable on first boot only on Btrfs roots. Redundant timeshift was
   dropped (snapper is the single tool).
2. Graceful agentic assistant. New shadowfetch-assistant: hardware-aware local-AI
   setup with in-app progress (no raw terminal), a local Ollama chat pane over
   127.0.0.1, and guided recipes. The Welcome first-run hands off to it. Runs
   fully offline; no account, no telemetry.
3. Crisp graphics. Rebuilt Umbra wallpapers, Plymouth, GRUB and SDDM themes, a
   real scalable vector emblem (the roadmap blocker), and the 4K default
   wallpaper. The SDDM login theme is now genuinely Shadowfetch (was stock Breeze
   metadata).
4. Deeper hardening. sysctl (kptr/dmesg/ptrace/bpf/rp_filter, protected_*) and a
   conservative kernel-module blacklist (dccp/sctp/rds/tipc plus legacy
   filesystems).
5. License and source compliance. Published LICENSES.md and a written source
   offer; a signed source tarball ships alongside the release; the unused empty
   APT source index was removed.

## Validation (QEMU/KVM)
- Live boot to multi-user: 0 failed systemd units.
- Feature audit: grub-btrfs hook + daemon + unit present; @snapshots subvolume in
  the installer; snapper present; apt pre-snapshot hook present; hardening applied
  (kptr_restrict=2, dmesg_restrict=1); assistant + Control Center byte-compile;
  Calamares branding 2.0.0; SDDM de-Breezed; 5 Umbra 4K wallpapers; license and
  source docs present.
- Stress: sequential 1 GiB write 2.6 GB/s, read 8.1 GB/s; clean poweroff.

## Publication order (safe)
APT repo (pool then dists), GPG key, source tarball, and ISO checksum/signature
published first; the 4.2 GB ISO last; public reachability verified; only then the
prior 1.9.0 ISO pruned from R2. The distro worker's latestRelease() flips
/linux/verify to 2.0.0 automatically once the ISO lands.

## Website
- All /linux pages bumped to 2.0.0 (version, SHA-256, size, apt package rows).
- New /linux/licensing page and footer link (license + written source offer).
- Real bug channel (GitHub issues + support@shadowfetch.com) on known-issues.
- Keyserver out-of-band note on /linux/security.
- Fixed the /linux/apt trailing-slash link (was 404).
- Added SoftwareApplication JSON-LD to /linux.
- Fresh 2.0.0 screenshots (desktop, assistant, welcome, apps menu, control
  center, agent studio, terminal).
- Zone-level HSTS enabled (max-age 15768000, includeSubDomains).

## Known limitations
- No Microsoft-signed Secure Boot chain (unchanged; under "Later").
- The full ISO is larger than 4 GiB; write to USB with dd or Etcher, not a FAT32
  file copy.
