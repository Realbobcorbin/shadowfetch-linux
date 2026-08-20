# Shadowfetch Linux 2.1.5 claim/source ledger

This ledger keeps the website, GitHub, Archive.org, and release notes tied to
checked source and exact-artifact evidence. Development work is not a release.

## Release state

- Development target: Shadowfetch Linux 2.1.5 Fire Edition, codename `umbra`.
- Public stable release: 2.1.4.
- No 2.1.5 hash, signature, size, availability, or PASS claim is valid until the
  final ISO and every required prepublication case are independently verified.

## Authoritative sources

| Claim | Source |
|---|---|
| Version, codename, package list, and ISO filename | `Makefile` |
| User-visible scope and known limits | `docs/RELEASE-2.1.5.md` |
| Buzz, coding-agent, and NVIDIA upstream locks | `qa/2.1.5/upstream-buzz.json`, `qa/2.1.5/upstream-codex.json`, `qa/2.1.5/upstream-coding-agents.json`, `qa/2.1.5/upstream-nvidia.json` |
| Required release evidence | `qa/2.1.5/acceptance.json` |
| Guide privacy, verdict, and report contract | `packages/shadowfetch-defaults/data/usr/bin/shadowfetch-passport` |
| Guide desktop and live-session entry points | `packages/shadowfetch-control-center/data/usr/share/shadowfetch/control-center/sfcc/guide_page.py`, `packages/shadowfetch-welcome/src/shadowfetch-welcome` |
| Buzz launcher and Wayland guard | `packages/shadowfetch-defaults/data/usr/bin/shadowfetch-buzz` |
| Coding-agent opt-ins, pinned artifact verification, user-level setup, and authentication boundaries | `packages/shadowfetch-welcome/src/shadowfetch-welcome`, `packages/shadowfetch-defaults/data/usr/bin/shadowfetch-codex`, `packages/shadowfetch-defaults/data/usr/bin/shadowfetch-code-agent`, `packages/shadowfetch-defaults/data/usr/share/doc/shadowfetch/CODING-AGENTS.md`, `qa/2.1.5/upstream-codex.json`, `qa/2.1.5/upstream-coding-agents.json` |
| Final hash, package inventory, VM results, and stress results | Final 2.1.5 evidence bundle |
| Public website, GitHub, and Archive.org state | Fresh postpublication probes |

## Guardrails

- Keep `https://www.shadowfetchlinux.org` and
  `https://github.com/ShadowfetchLinux/shadowfetch-linux` canonical.
- Keep verified raw APT and ISO routes unchanged until replacements are tested
  as raw, cache-correct, byte-identical endpoints rather than HTML routes.
- Do not reuse 2.1.4 screenshots, hashes, logs, or test results as 2.1.5 proof.
- Do not call Guide private or local-only until the final-ISO process and
  network audit proves no implicit write, upload, privileged repair, or
  identifier escape.
- Do not infer physical GPU support from virtual graphics.
- Do not claim a model is bundled; Buzz owns recommendation and consented
  download in **Settings > Compute**.
- Describe every coding agent as optional and independent. Do not imply any is
  bundled, pre-authenticated, included with a free plan, or required for Buzz.
- Never embed, copy, or publish a coding-agent token, API key, or account
  credential. Authentication remains inside each tool after explicit install.
- Do not imply affiliation with or endorsement by Block.
