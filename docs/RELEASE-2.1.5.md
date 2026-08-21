# Shadowfetch Linux 2.1.5 Fire Edition

Codename: Umbra

Status: RELEASED 2026-08-20. Every required prepublication case in
`qa/2.1.5/acceptance.json` passed against the exact final ISO recorded below,
and the public artifacts were verified after publication.

- ISO: `shadowfetch-2.1.5-amd64.iso`
- Size: 3,968,471,040 bytes (3.97 GB / 3.70 GiB)
- SHA-256: `848f043e4d6f85c3607e7034ba911a1ce8b4a317674feebef8b07fcd8f531c24`
- Detached signature: `shadowfetch-2.1.5-amd64.iso.asc`
- Signing key: `8F13 CE15 35EE 1F4A 2916  A1F7 3C5C 900B 7BE8 0CA1`
- Canonical website: https://www.shadowfetchlinux.org
- Download page: https://www.shadowfetchlinux.org/download
- Signed ISO (freeze host; this is the URL that returns the image bytes): https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso
- Checksum sidecar: https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso.sha256
- Detached signature: https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso.asc
- Signing key: https://www.shadowfetch.com/linux/shadowfetch.gpg.asc (also https://www.shadowfetchlinux.org/shadowfetch.gpg.asc)
- Mirror: https://archive.org/details/shadowfetch-linux-2-1-5

## Release goal

Give the Fire Edition a reason to begin or continue a Linux journey: the system
should explain what works before installation and point to a safe, existing
repair path afterward. Shadowfetch Linux 2.1.5 keeps one optional local-AI path
through Buzz, adds independent options to install Codex, Claude Code, Grok
Build, or Cursor Agent,
keeps model downloads and cloud sign-in under the user's control, and preserves
the verified update and recovery workflow.

## Headline feature: Shadowfetch Guide

**The Linux desktop that can explain itself.**

**Before you install, it proves what works. After you install, it helps fix what
doesn't.**

Shadowfetch Guide begins with a local System Passport for graphics, networking,
audio, firmware, memory, storage, recovery readiness, installed-system health,
and local-AI capacity. It is available from the live Ignition screen and remains
the first section of Control Center after installation or upgrade.

The Passport is deterministic and read-only. It does not upload data, install a
driver, alter a setting, or give a model unrestricted root access. Its public
schema is built from an allowlist and omits host identity, account names, network
identifiers, hardware serials, and filesystem identifiers. Highlighted checks
route to the existing Drivers, Phoenix, Software & Updates, or Local AI pages,
where normal confirmation and polkit boundaries remain in force. A user may
explicitly save the redacted report as HTML or JSON.

## Planned changes

- Ship Shadowfetch Guide and its private System Passport in the live and
  installed desktop.
- Make Guide the first Control Center section and expose **Check this computer**
  from both Ignition and Welcome.
- Make `https://www.shadowfetchlinux.org` the canonical product website.
- Make `https://github.com/ShadowfetchLinux/shadowfetch-linux` the canonical
  source and issue-tracking repository.
- Preserve the currently verified APT and ISO object routes until equivalent
  raw routes on the new domain are proved byte-for-byte in release acceptance.
- Guard Buzz Desktop on Plasma Wayland against the WebKitGTK DMA-BUF rendering
  freeze while preserving explicit user overrides and the normal X11 path.
- Offer Codex, Claude Code, Grok Build, and Cursor Agent together beside Buzz
  during first-run setup. Keep all four choices unchecked, pin and verify each
  release, install only for the desktop user, and leave authentication to each
  tool itself.
- Bump every Shadowfetch-owned binary and source package to `2.1.5-1` and build
  them into a freshly signed Umbra repository.
- Capture new release screenshots from the exact final ISO. Images from 2.1.4
  and supplied promotional artwork are comparison or marketing references, not
  runtime evidence.

## AI and agent contract

- Buzz remains optional and is offered during first-run setup.
- No open model is bundled in the ISO.
- Buzz recommends and downloads a model only after the user confirms in
  **Settings > Compute**.
- The relay and shared-compute endpoints remain loopback-only by default.
- Every coding agent remains optional and independent of the local Buzz model
  path. The four choices may be selected separately or together.
- Shadowfetch includes no vendor credential. Each coding agent offers its own
  supported sign-in only after the user explicitly installs and opens it.
- One coding-agent download or authentication failure cannot block another
  selected tool, the base operating-system setup, or a working Buzz setup.
- Shadowfetch exposes `grok` and `cursor-agent`, not the conflicting generic
  `agent` aliases advertised by both upstream installers.
- Retired agent and secondary model runtimes do not return to the active image
  or menus.

## Upgrade from 2.1.4

The supported in-place path is the signed Shadowfetch APT repository:

```bash
sudo apt update
shadowfetch-update
```

Release acceptance must exercise that transaction from a real 2.1.4
installation, preserve user files and Buzz state, reboot cleanly, and show no
failed services. The 2.1.4 recovery and removal-safety checks remain in force.

## Deferred to 2.2.0

The offline-oriented `shadowfetch-hardware` repair helper under `next-release/`
remains staged and unshipped. Guide 2.1.5 explains measured state and opens
existing safe tools; autonomous repair plans and new model runtimes remain
outside this release.

## Release gates

- Pass source, behavior, syntax, ShellCheck, secret, and retired-runtime scans.
- Prove the Passport omits seeded host, account, network, serial, PCI-slot, and
  filesystem identifiers; prove the check itself performs no upload or repair.
- Exercise Guide in both the final live session and a real 2.1.4-to-2.1.5
  upgraded installation, including redacted HTML and JSON export.
- Build and inspect every 2.1.5 binary and corresponding source package.
- Verify the signed local repository, package install, upgrade, and rollback.
- Verify the exact ISO structure, checksum, detached signature, BIOS, and UEFI.
- Complete clean BIOS and encrypted UEFI installations and reboot tests.
- Exercise Buzz setup, model consent, real inference, failure recovery, relay
  isolation, and Plasma Wayland responsiveness.
- Exercise all four unchecked coding-agent choices, select-all behavior,
  artifact and version verification, user-level ownership, menu integration,
  failure isolation, cancellation, retry, and authentic first-launch sign-in
  screens without preloaded credentials.
- Run sustained CPU, memory, storage, network, graphics, Buzz, reboot, and
  filesystem stress checks.
- Capture fresh 2.1.5 screenshots and inspect them for stale branding, blank
  windows, overlap, clipping, and misleading model state.
- Stage and verify website, GitHub, and Archive.org metadata before publication.
- Publish only after all required prepublication cases are green, then verify
  every public artifact and canonical URL before marking 2.1.5 released.
