# live-build archives

`shadowfetch.list.chroot` points the chroot's apt at a local HTTP server
serving the freshly-built `repo/` directory at `http://127.0.0.1:8089/`.
The `Makefile` `iso` target starts that server before invoking `lb build`
and tears it down on exit.

`shadowfetch.list.binary` is the apt sources entry that ships *inside*
the final ISO, pointing at the public APT repo at
`https://shadowfetch.com/linux/apt/`. End users get incremental updates
through that URL.

The matching `.key.chroot` / `.key.binary` files (GPG public key, armored)
are copied here by `make iso` from `repo/shadowfetch.gpg.asc`. They're
intentionally not committed — they're regenerable from the GPG keyring.
