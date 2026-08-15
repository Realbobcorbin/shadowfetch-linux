# Shadowfetch Linux 2.1.4 Fire Edition

Codename: Umbra

Status: RELEASED 2026-08-10. Every required item in `qa/2.1.4/acceptance.json`
holds fresh passing evidence against the published ISO
(`shadowfetch-2.1.4-amd64.iso`, SHA-256
`81a906788ec48150d4a4527b4d9e7b09a974d3d577f1bd32ba3f333df8a1a86b`,
3,968,475,136 bytes, detached signature by key
`8F13CE1535EE1F4A2916A1F73C5C900B7BE80CA1`). Three candidates were built during
release QA; visual QA caught a duplicated launcher menu in the first and the
physical-GPU gate caught a driver-transaction conflict in the second — both
fixed at the source and fully re-verified. The signed evidence bundle hash is
recorded in the acceptance manifest.

## Release goal

Turn the 2.1.3 local-AI workstation into a coherent flagship experience:
working graphics first, a polished Fire Edition desktop, and one clear choice
for Buzz. Setup must fail safely, explain recovery, and never report success
before the verified Buzz package and private relay have passed their checks.
Buzz itself owns open-model recommendation, download, progress, and serving.

## First-run local AI

- Replaces Hermes and OpenClaw choices with Buzz.
- Offers verified Buzz setup or an explicit not-now choice.
- Downloads Buzz Desktop 0.5.8 from Block's official release and verifies SHA-256
  `ca67a81c2c75e908b38039a6571cf87aa38112a0ef06881fc50049a8b0b58c67`.
- Simulates the Buzz package transaction, refuses package removals, preserves an
  installed newer version, and verifies the installed package afterward.
- Pins Buzz Relay 0.2.1 and every supporting container by immutable image digest.
- Starts the rootless Buzz relay bound only to `127.0.0.1:3000`.
- Stores generated relay secrets in owner-only files and keeps relay data in
  rootless Podman volumes.
- Opens the official Buzz client after setup. In **Settings > Compute**, Buzz
  surveys the hardware, preselects its recommended open model, downloads only
  after the user enables sharing, and serves through `127.0.0.1:9337`.
- Ships no second model picker, model registry, browser-chat stack, or external
  model runtime.
- Keeps the first-run wizard incomplete when setup fails or is cancelled so the
  user can retry without a false completed state.

## Graphics

- Removes the Debian-550-era new-GPU dead end.
- Detects hardware rendering separately from llvmpipe and handles hybrid or
  multi-GPU systems without treating one software renderer as total failure.
- Verifies NVIDIA's Debian 13 repository keyring package before installation.
- Uses `nvidia-driver-assistant --distro debian:13` to select the supported
  branch and open/closed kernel module flavor for the detected card.
- Simulates every NVIDIA package transaction, refuses package removals, and
  applies the assistant's strict allowlisted recommendation with `--no-remove`.
- Installs matching running-kernel headers, enables DRM KMS, handles hybrid
  graphics conservatively, and records non-interactive Secure Boot work for the
  next reboot instead of hanging.
- Creates Btrfs Phoenix snapshots around driver changes when supported.
- Requires post-reboot `nvidia-smi`, kernel-module and Vulkan verification
  before reporting the graphics path ready.

## Menus and control surfaces

- Keeps the seven-section Fire Edition launcher with refreshed Local AI entries.
- Renames AI and Agents to Local AI.
- Leads with Buzz shared compute, private AI workspaces and health/privacy
  checks.
- Removes active Hermes and OpenClaw installers, launchers, setup screens,
  documentation and diagnostics from the image source.
- Keeps long setup work cancellable and prevents accidental window closure while
  Buzz and its private relay are being installed.

## Update and recovery safety

- Simulates every full upgrade before applying it and refuses every unverified
  removal. The measured Plasma 6.6 to 6.7 replacement pair is accepted only
  when both replacement packages are present in the same solver plan.
- Verifies the complete install/removal plan a second time immediately before
  applying it and stops if the plan changed.
- Refuses to run while dpkg or another package manager is active, with low disk,
  or with unsuitable power conditions.
- Uses download retries and timeouts, `--no-remove` whenever no verified
  replacement is required, one automatic Phoenix pre/post pair from Debian's
  `80snapper` hook, and post-upgrade health checks.
- Retires only the signed distro-managed 2.1.3 local-AI package manifest,
  including Debian's `llama.cpp-services` transition package when a direct APT
  upgrade introduces it. Package payloads are removed, while personal
  workspaces and downloaded model data are preserved. Direct APT upgrades use
  the same strict cleanup at the next boot.
- Writes durable logs and recovery pointers without putting credentials in the
  release tree.

## Upgrade from 2.1.3

The 2.1.3 Safe Update executable predates Debian Testing's Plasma package rename
and correctly refuses that removal plan. Install the signed 2.1.4 updater first,
using the removal-free bridge, and then run the new validated transaction:

```bash
sudo apt update
sudo apt-get --no-remove install shadowfetch-defaults
shadowfetch-update
```

The bridge is simulated and tested against a genuine 2.1.3 installation. The
second command upgrades the connected Shadowfetch metapackages without removing
anything; `shadowfetch-update` then owns the complete Debian and Shadowfetch
transaction, Phoenix recovery point, legacy-package retirement, and health check.

## Release gates

- Pass all focused source and behavior tests, ShellCheck and `git diff --check`.
- Build and inspect every 2.1.4 binary and corresponding source package.
- Start a disposable rootless Buzz stack and pass ordered database, cache,
  object-store and relay readiness checks on loopback only.
- Confirm the exact verified Buzz Desktop package contains its native mesh-LLM
  runtime, then exercise Buzz's hardware recommendation, model download,
  loopback model inventory and a real local prompt in the final VM.
- Verify ISO BIOS and UEFI metadata, checksum and detached signature.
- Boot and install the candidate in clean BIOS and UEFI virtual machines.
- Upgrade an overlay clone of a real 2.1.3 installation and preserve user data.
- Exercise offline/reconnect, low-resource, occupied-port, cancellation,
  interrupted-update, rollback and repeated-reboot paths.
- Exercise keyboard navigation, screen scaling and readable error/retry states.
- Run sustained CPU, memory, disk, network, Buzz model and relay workloads, then pass
  filesystem, journal, service and reboot health checks.
- Capture fresh screenshots from the final ISO. Buzz evidence must show the real
  Buzz Desktop client connected to its local relay inside Shadowfetch; a pasted
  promotional image is reference material only, not runtime proof.
- Record physical NVIDIA, AMD/Intel Mesa and Secure Boot evidence separately;
  virtualization must never be presented as physical-GPU proof.
- Publish only after the acceptance manifest is fully green, then re-download
  and verify every public ISO, checksum, signature, repository and rollback URL.
