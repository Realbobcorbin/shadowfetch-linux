# Contributing

Pull requests to the build scripts, in-house packages, docs, QA gates, and the
release Worker are welcome. Feature work that changes Control Center, Buzz,
Phoenix, Fireproof, or the first-run agent installers should come with a
reproducer or a `make source-gate` failure that the change fixes.

## Before you open a PR

```sh
make source-gate
```

That is the same source/test/secret gate the Makefile documents. You do not
need the signing key or Cloudflare credentials to run it.

Do not commit:

- ISO images, torrents, or other multi-gigabyte release blobs
- `.deb` / `dpkg-buildpackage` artifacts
- GPG private keys, Cloudflare tokens, R2 keys, or `.env` files
- password CSVs, unredacted `shadowfetch-health` dumps, or private logs

## Bugs and hardware reports

Use GitHub Issues with the **Bug report** or **Hardware report** form:

https://github.com/ShadowfetchLinux/shadowfetch-linux/issues

A good bug report includes the exact ISO filename and whether the checksum
matched, UEFI vs BIOS and Secure Boot state, CPU/GPU/RAM/disk/Wi-Fi, and
redacted `shadowfetch-health --json` output.

## License

By contributing you agree your changes ship under this repository's licenses:
GPL-3.0-or-later for the tree (see `LICENSE`), plus each package's
`debian/copyright`. The Shadowfetch and Umbra names, logos, and wallpapers
remain reserved; see `TRADEMARKS.md`.
