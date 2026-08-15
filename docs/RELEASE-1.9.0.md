# Shadowfetch Linux 1.9.0 Release Report

Release: Shadowfetch Linux 1.9.0 "Umbra - Command Center"  
Release date: July 12, 2026  
Architecture: amd64  
ISO size: 4,486,635,520 bytes

## Release identity

- ISO: `shadowfetch-1.9.0-amd64.iso`
- SHA-256: `36782d01da09da90915d5147910241acfcd56849e4b3ca5c01abccadeebca28d`
- Signing fingerprint: `8F13 CE15 35EE 1F4A 2916 A1F7 3C5C 900B 7BE8 0CA1`
- Signature identity: `Shadowfetch Project <signing@shadowfetch.com>`
- Boot support: hybrid BIOS and UEFI image
- Kernel in tested live environment: `7.1.3+deb14-amd64`

## What changed

### Command Center

The new native Shadowfetch Control Center presents the common system jobs in one compact Plasma application: safe updating, health checks, first-run setup, graphics, recovery, snapshots, and agent tooling. The 1280x800 release capture was checked for readable labels, stable card geometry, icon fallbacks, and non-overlapping controls.

### Safer system maintenance

`shadowfetch-update` checks power, storage, networking, package locks, and package consistency before changing the system. It records the run, creates Btrfs snapshots when supported, and finishes with a health report. `shadowfetch-recovery` provides guided recovery actions without silently performing destructive changes.

### Agent Studio

`shadowfetch-agent-workspace` creates a private workspace containing operating rules, active tasks, durable memory, a work journal, artifacts, logs, and scratch space. It can create a matching isolated Hermes profile. `shadowfetch-agent-doctor` audits readiness and exposure risks; `shadowfetch-agent-tools` guides optional browser automation and container isolation for Hermes and OpenClaw.

Large browser runtimes and agent frameworks remain opt-in. This keeps the installed system lean and avoids enabling network-facing automation services without the user's choice.

### Browser migration

The new Browser Migration assistant addresses the most actionable part of early user feedback. It:

- validates Netscape-format bookmark HTML before import;
- validates password CSV files for the required `url`, `username`, and `password` columns;
- stages copies in a private `~/Browser Import` directory with restrictive permissions;
- grants the Brave Flatpak temporary read-only access only to that directory when needed;
- opens the browser's bookmark or password import page; and
- removes staged files and the temporary filesystem permission during cleanup.

This addresses common file-format and Flatpak-access causes. It does not claim that every upstream browser import defect is fixed.

### Simpler local AI setup

The recommended setup now selects one local model based on available memory and sets up local web chat by default. The wider model catalog, cloud providers, and multi-agent choices are presented as advanced options instead of first-run requirements. Local processing remains the recommended privacy-preserving path.

## Validation

### Build and package gates

- Python byte-compilation passed.
- Shell syntax and ShellCheck gates passed.
- Desktop entry validation passed.
- Seven versioned 1.9.0 packages built successfully.
- The APT repository metadata was regenerated and signed.
- The ISO checksum and detached GPG signature were verified against the final artifact.

### VM functional checks

The live image booted under QEMU/KVM with networking, the `shadow` live user, sudo access, and the complete command set. Health JSON generation, Control Center CLI mode, Agent Studio workspace creation, and Browser Migration command availability passed in the VM. Separate temporary bookmark HTML and password CSV fixtures passed validation, staging, permission, and cleanup checks on the Linux build host.

### Full stress run

Configuration: 6 vCPU, 8 GiB RAM, 20 GiB virtio qcow2 stress disk, QEMU/KVM.

- CPU/matrix verification: passed
- Memory verification: passed
- 1 GiB sequential write: approximately 1.0 GB/s in the test VM
- 1 GiB sequential read: approximately 6.2 GB/s from the VM/cache path
- 120-second random mixed I/O: 36.0k read IOPS / 141 MiB/s and 15.4k write IOPS / 60.3 MiB/s
- Combined 120-second CPU, memory, and I/O run: passed
- Script failures: 0
- QEMU exit code: 0

An intermediate no-radio VM run reported `rfkill-unblock.service` as failed because no rfkill device existed. The unit was changed so absent radio hardware is a successful no-op. The exact final ISO was then retested for 120 seconds with 6 CPU, 2 memory, and 2 I/O workers: all 10 stress workers passed, none failed or skipped, and the final failed-service gate returned `SERVICE_AUDIT_PASS`.

## Known limitation

The release supports UEFI boot but does not ship a Microsoft-signed Secure Boot chain. Secure Boot may need to be disabled on systems that require a trusted signed bootloader. The website and hardware guide state this directly.

## Publication order

The signed APT repository, public key, screenshots, checksum, and detached signature were published before the ISO. The previous ISO remained available until the 1.9.0 object passed public size, range, checksum, signature, and page-level checks. Only then was the older release removed.

## Publication result

- Live release: `https://www.shadowfetch.com/linux/`
- Website build: `2026.07.12.8`
- Cloudflare Worker version: `1c1d6d06-0c61-4102-a525-16115ba8aded`
- Public range response: `206 Partial Content`
- Full public re-download: approximately 43 MiB/s average during the verification run
- Full public SHA-256: matched the signed release checksum
- Public detached signature: good EdDSA signature from the Shadowfetch signing identity
- Obsolete storage removed after verification: 200 objects / 4,600,140,788 bytes
- Retained release inventory: the 1.9.0 ISO, checksum, signature, and seven packages referenced by the live APT index
- Previous 1.8.1 ISO after pruning: `404 Not Found`

Responsive production QA covered all nine main Linux routes at a 390 x 844 mobile viewport and the four primary routes at a 1440 x 900 desktop viewport. Every checked page had one H1, no broken images, and no horizontal document overflow. The compact mobile navigation exposes all nine destinations without resizing the header, and the homepage leaves the next section visible in the first mobile viewport.
