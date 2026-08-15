# Fire Roadmap — deferred beyond 2.1.2 by design

Founder-cut and spec-cut items, recorded 2026-07-30 so nothing is lost. Every entry
below was deliberately kept OUT of 2.1.2 "Fire Edition"; the release ships only what
its QEMU matrix proves. Source: the founder's 12-item vision (top-8 shipped) plus the
v1-vs-roadmap splits in the pillar and additions specs.

## Founder items not in the 2.1.2 top-8
- **Fire Terminal** — polished default prompt, git branch, system-health indicator,
  command suggestions, optional AI command explanation, destructive-command warnings,
  and the `sf-*` helper family (sf-health, sf-update, sf-repair, sf-snapshot,
  sf-drivers, sf-agents, sf-ignite). Great demo surface; pairs with Fireproof + Phoenix
  CLIs that 2.1.2 already ships (`fireproof`, `phoenix-*`).
- **Flameguard privacy dashboard** — microphone/camera access, active connections,
  listening ports, recently launched apps, firewall status, DNS configuration,
  telemetry status, local-vs-cloud AI usage. Fits the brand perfectly; needs its own
  privacy-honest data-source recon (what is knowable without becoming a monitor itself).
- **Shadowfetch diagnostics report** — one-click privacy-safe support bundle with
  preview-before-save. 2.1.2 ships the Phoenix recovery-report as the seed; the full
  tool generalizes it.
- **Fire Edition desktop widgets** — compact panel widget: temps, agent activity,
  update status, snapshot status, network, loaded model. One widget, not a gauge wall.

## Pillar spec deferrals (v1 shipped the mechanism-backed subset)
- Ember: NVIDIA clock pinning (nvidia-smi -lgc), per-app `ember-run` wrapper,
  tuned-based deep profiles, fan-curve override, user-editable pause list,
  whole-wall power readout (no mechanism exists).
- Firewatch: per-process/per-agent network column, non-llama runtime metrics
  (ollama/vLLM), out-of-box NVIDIA telemetry from the live ISO, per-process
  temperature attribution (no OS mechanism), treemap view of the heat-map.
- Phoenix: ext4 "Phoenix Lite" (timeshift-rsync), @home snapshot protection,
  one-click "make this Flame permanent" from inside an overlay session,
  scheduled timeline snapshots, qgroup space accounting.
- Fireproof: the auto-hold engine for repeated-failure packages (v1 breaks the
  rollback carousel with the package-set hash), Discover full replacement.
- Ignition: Calamares packagechooser pre-pick during install (config-only UX sugar;
  Welcome-first shipped as the single code path).

## The big one
- **Agent Oasis for Linux** — a rewrite, not a port (macOS SwiftUI, Keychain,
  LocalAuthentication; ~4,000 UI lines to Qt/Kirigami, libsecret, polkit). Honest
  estimate 40–60 days. The MIT license and the Foundation-only core (~1,500 lines that
  compile on Swift-for-Linux) make it credible. 2.1.2's Agent Workspace template is the
  bridge; Oasis becomes the flagship workspace when it lands.

## Standing candidates from the quality sweep
- Automate the apt-repo re-sign on a timer (14-day Valid-Until; manual today).
- Real full-image packages.manifest generation wired into every release (2.1.2 restores
  it; keep it automatic).
