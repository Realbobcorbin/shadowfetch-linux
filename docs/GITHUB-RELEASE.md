# GitHub release notes (paste template)

GitHub's per-file release-asset limit is 2 GiB. The Shadowfetch ISO is ~4 GB,
so **do not attach the ISO** to a GitHub Release. Attach only the small
verification files (`.iso.sha256`, `.iso.asc`) if you want them on the tag;
the signed image itself stays on the freeze host.

The current tag is `v2.1.5`. The notes already published there can be replaced
with the body below if they drift. Future tags can start from this template.

Checksums in-tree: [`SHA256SUMS`](../SHA256SUMS) (signed as `SHA256SUMS.asc`).
The public key copy in this repo is [`shadowfetch-release.asc`](../shadowfetch-release.asc).

## Body for v2.1.5

~~~~markdown
## Shadowfetch Linux 2.1.5 «Umbra» — Fire Edition

GitHub does not host the ISO (4 GB; GitHub's per-file limit is 2 GiB).
Download the signed image from the freeze host, then verify it.

### Download
- **ISO:** https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso — 3,968,471,040 bytes (3.97 GB / 3.70 GiB), BIOS + UEFI hybrid
- **SHA-256:** `848f043e4d6f85c3607e7034ba911a1ce8b4a317674feebef8b07fcd8f531c24`
- **Checksum sidecar:** https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso.sha256
- **Signature:** https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso.asc
- **Signing key:** https://www.shadowfetch.com/linux/shadowfetch.gpg.asc
- **Fingerprint:** `8F13 CE15 35EE 1F4A 2916  A1F7 3C5C 900B 7BE8 0CA1`
- **Verify guide:** https://www.shadowfetchlinux.org/verify
- **Download page:** https://www.shadowfetchlinux.org/download
- **Archive.org mirror:** https://archive.org/details/shadowfetch-linux-2-1-5

### Verify

```sh
curl -LO https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso
curl -LO https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso.sha256
curl -LO https://www.shadowfetch.com/linux/download/shadowfetch-2.1.5-amd64.iso.asc
curl -LO https://www.shadowfetch.com/linux/shadowfetch.gpg.asc
gpg --import shadowfetch.gpg.asc \
  && gpg --verify shadowfetch-2.1.5-amd64.iso.asc shadowfetch-2.1.5-amd64.iso \
  && sha256sum -c shadowfetch-2.1.5-amd64.iso.sha256
```

A GPG "not certified with a trusted signature" warning only means you have not
personally trusted the key. Compare the fingerprint before you trust the download.

Full notes: https://github.com/ShadowfetchLinux/shadowfetch-linux/blob/main/docs/RELEASE-2.1.5.md
~~~~
