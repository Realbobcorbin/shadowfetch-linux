# Shadowfetch Linux 2.1.4 claim/source ledger

This ledger keeps the website, GitHub release, Archive.org record, and release
notes tied to checked source and final evidence. It must not be used to imply
that a development candidate has passed or been published.

## Release state

- Development target: Shadowfetch Linux 2.1.4 Fire Edition, codename `umbra`.
- The public release remains 2.1.3 until every prepublication acceptance item
  is evidenced and the 2.1.4 artifacts are independently verified.
- No final 2.1.4 ISO hash, signature, PASS statement, or public URL exists until
  the final reproducible build and publication probes complete.

## Authoritative sources

| Claim | Source |
|---|---|
| Version, codename, package build list, and ISO filename | `Makefile` |
| User-visible changes and known limitations | `docs/RELEASE-2.1.4.md` |
| Buzz tag, commit, Linux package URL and hash, required binaries, and release features | `qa/2.1.4/upstream-buzz.json` |
| NVIDIA Debian 13 repository key, driver-assistant build, supported-GPU table, RTX 5080 policy, and package hashes | `qa/2.1.4/upstream-nvidia.json` |
| Required prepublication and postpublication evidence | `qa/2.1.4/acceptance.json` |
| Buzz installation, checksum verification, dependency simulation, and no-remove policy | `packages/shadowfetch-defaults/data/usr/libexec/shadowfetch-buzz-provision` |
| Loopback-only relay and immutable service images | `packages/shadowfetch-defaults/data/usr/share/shadowfetch/buzz/compose.yml` |
| Welcome flow, skip behavior, cancellation, and completion semantics | `packages/shadowfetch-welcome/src/shadowfetch-welcome/` |
| Hardware survey and NVIDIA guidance | `packages/shadowfetch-hwscan/`, `qa/2.1.4/upstream-nvidia.json`, and the final physical-hardware evidence dossier |
| Final ISO hash, detached signature, package inventory, boot tests, and stress results | Final 2.1.4 release evidence dossier |
| Website hero and top-navigation Buzz link | Final deployed website source and public browser probes |

## Buzz wording

- Buzz is optional and is offered during first-run setup.
- Buzz owns model recommendation and download in its own Settings > Compute
  flow. Shadowfetch does not ship a model or a competing model manager.
- The official Buzz repository is `https://github.com/block/buzz`.
- The website may describe Buzz as an available open-source project, but must
  not imply affiliation with or endorsement by Block.

## Guardrails

- Do not call 2.1.4 current, passed, signed, shipped, or available before final
  acceptance evidence and public probes exist.
- Do not reuse hashes or screenshots from an earlier candidate.
- Do not claim installs, users, market share, DistroWatch conversion, or support
  for every hardware combination.
- Do not claim Secure Boot support unless a signed-boot test is added and passes.
- Do not infer physical NVIDIA behavior from a virtual GPU test. Physical GPU
  claims require hardware evidence.
- Keep Buzz relay and model endpoints on loopback by default.
- Do not claim a local model is preinstalled. The user explicitly approves the
  Buzz install and Buzz performs model selection and download.
- Do not publish a historical redirect, ISO, checksum, signature, screenshot,
  or release record until the exact public object has been uploaded and probed.
