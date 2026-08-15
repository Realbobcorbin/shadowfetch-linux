# Shadowfetch Linux 2.1.1 "Umbra"

2.1.1 is a correctness release for the system identity. The 2.1.0 image identified itself as 2.0.1 in os-release, `/etc/issue`, Calamares branding, the SDDM theme, and helper tools because those surfaces derived from `/usr/share/shadowfetch/version`, and that file was still a hand-maintained literal. The build now stamps the version from the Makefile, and the tools read it at runtime.

The release also keeps the 2.1.0 package line aligned: `shadowfetch-meta` rebuilt with members pinned to 2.1.0-1 for 2.1.0, while 2.1.1 corrects the reporting layer across branding, defaults, meta, themes, and welcome packages. The release collector used for this repo update identifies the public release as 2.1.1, ISO `shadowfetch-2.1.1-amd64.iso`, codename `umbra`, with integrity status PASS. Publication approval is a separate owner decision.

## User-visible change

The installed system and installer surfaces should report the current Shadowfetch Linux version instead of an older one.

## Why it matters

Version mismatches make verification, bug reports, hardware reports, and release support harder. A user checking the ISO, installer, desktop, and helper tools should not see conflicting release identities.

## Verify this release

Download the ISO, checksum, detached signature, and signing key from the release/download page, then run the five-line verification block in the README. The current public SHA-256 is:

`f5fe0f20dd24176839d0443f75ac4110587dff1a369785abdbe2121e213afdba  shadowfetch-2.1.1-amd64.iso`

## Known caveats

- Secure Boot is not signed yet.
- Debian testing remains the base package ecosystem.
- Local AI needs real RAM and disk headroom; the recommended setup chooses one model, but advanced models still vary by size.
- Publication approval is separate from integrity status; do not turn an integrity PASS into an owner-approval claim.

## Prior context

- 2.1.0 added `shadowfetch-facts`, a read-only inventory with fact sources for bug reports and hardware-aware tooling.
- 2.0.1 fixed installer/discoverability problems found from public-review reading: AGENTS.md is shipped uncompressed, the local-AI menu entry is visible in KDE, seven on-device AI applications are grouped under Local AI, and helper tools answer `--help`/`--version` before side effects.
- 2.0.0 "Bedrock" introduced boot-to-snapshot update resilience, the graceful agentic assistant, the crisp Umbra graphics refresh, deeper hardening, and published license/source compliance materials.
- 1.9.0 "Command Center" introduced Control Center, Safe Update, Agent Studio, system-health reporting, Browser Migration, and simpler local-AI setup.
