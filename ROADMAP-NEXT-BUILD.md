# Shadowfetch Linux — Next-Build Idea Backlog (post-1.0.6)

> **Historical.** Compiled 2026-05-29 against 1.0.6. It is not the 2.1.5 plan.
> Several items below (local AI, Btrfs snapshots, Calamares) later shipped in a
> different form. Current direction: [`docs/FIRE_ROADMAP.md`](docs/FIRE_ROADMAP.md)
> and https://www.shadowfetchlinux.org/roadmap.

*Compiled 2026-05-29 from Reddit research across r/linux, r/linux4noobs, r/DistroHopping, r/unixporn, r/kde, r/linux_gaming, r/privacy, r/debian, r/selfhosted (4 parallel research sweeps). Filtered against what 1.0.6 "Umbra" already ships. Tags: **Impact** (★ demand) · **Effort** (E/M/H) · 🜂 = strong Shadowfetch brand fit.*

> **Hard constraint to respect:** 1.0.6's squashfs is already **3.1 GiB of the 4 GiB limit**. Heavy additions (Steam+Proton-GE ≈2 GB, AI tooling, models) must be **first-boot downloads via the Welcome app, NOT baked into the ISO** — both to stay under 4 GiB and to keep the image lean. This shapes the whole plan: bake *config*, download *bulk*.

> **✅ SHIPPED (2026-05-30):** **1.0.7 "Umbra Identity"** = Tier 3 (full graphite+gold visual identity: wallpapers, gold Plasma/Konsole, gold Plymouth, GRUB + SDDM themes). **1.0.8 "Polish & Protect"** = most of Tier 1 (media codecs, Flathub-in-Discover, UFW + MAC randomization + IPv6 privacy, ZRAM, Bluetooth LDAC, GTK-dark, font polish [Inter + Fira Code], nala/distrobox/podman, NVIDIA-resume modprobe, first-boot setup service). **1.0.9 "Quality of Life"** = deep Reddit-pain-point fixes (printing/scanning, SMB/NAS shares in Dolphin, KDE Connect, NTFS/exFAT, dual-boot clock fix, earlyoom anti-freeze, video/RAW thumbnails, CJK+MS fonts, 15s shutdown, ZRAM swappiness, journald cap, auto security/Flatpak updates, Baloo/numlock/clipboard/animation tuning, brightness/Fn/fingerprint) **+ a local-AI on-ramp** (`shadowfetch-ai` installs Ollama on demand, localhost-hardened). **1.1.0 "Local AI"** = the *full* private-AI stack — `shadowfetch-ai {setup|webui|status|stop}` now installs Ollama **+ Open-WebUI** (ChatGPT-style web chat) via hardened rootful podman (host-net, localhost-bound, auth, UFW-blocked, GPU-aware), with Setup + Web Chat menu launchers — plus KDE utility extras (filelight, kio-admin edit-as-root, partitionmanager, kio-gdrive, kfind, kompare). *Dropped — not in this Debian:* auto-cpufreq, JetBrains Mono Nerd Font (→ Fira Code), libfuse2/AppImage, ananicy-cpp, gutenprint/hplip/kimageformats; *tlp skipped* (conflicts with KDE's power-profiles-daemon). **Still open (next headline candidates):** **Btrfs snapshots + boot-to-snapshot rollback** (the #1 universal request), **Calamares installer** (Tier 2 — unlocks Btrfs + LUKS), deeper hardening (Tier 5 — TPM2/Secure Boot/USBGuard/dnscrypt), **gaming spin** (Tier 4 — Steam/Proton-GE/MangoHud), Welcome-app v2, and full NVIDIA suspend-enable (needs the driver baked in first). *(Shipped 1.0.7→1.1.0: visual identity, polish & protect, deep QoL, full local AI.)*

---

## ⭐ The 3 signature bets — what makes Shadowfetch *Shadowfetch*

These aren't just features other distros have; they're the ones that match the brand and that **no Debian+KDE distro ships well today.**

### 1. 🜂 "Shadowfetch AI" — a local, private AI stack out of the box
Ollama + Open-WebUI preinstalled as systemd services, **GPU-autodetected**, **localhost-bound + hardened** (UFW-blocked from LAN, AppArmor profile, Open-WebUI auth required). First-boot prompt: *"Download a starter model? [llama3.2:3b / phi4 / skip]"* — models pull on demand, never in the ISO.
- **Why it's the flagship:** you operate an AI-agent company. A privacy-first distro that ships *local* AI (no cloud, no account, no telemetry) is a genuine differentiator that gets written about. Demand on r/LocalLLM / r/selfhosted is high and climbing.
- **Impact ★★★ · Effort M · 🜂🜂🜂**

### 2. "Never breaks" — Btrfs root + automatic snapshots + boot-to-snapshot rollback
Btrfs with proper subvolumes (`@`, `@home`, `@snapshots`) + `timeshift-autosnap-apt` (or snapper) hooking `DPkg::Pre-Invoke` so **every apt op auto-snapshots** + `grub-btrfsd` so a broken upgrade is one reboot away from "Restore snapshot from before." This was the **single most-requested feature across all four sweeps** — the openSUSE/Garuda "killer feature" that no mainstream Debian distro ships.
- **Impact ★★★ · Effort M** (needs the installer / Btrfs layout — see Tier 2) **· 🜂**

### 3. 🜂 "Stealth by default" — privacy/security hardening that matches the name
A coherent hardened-by-default posture: MAC randomization, encrypted DNS, VPN kill-switch, FDE default, firewall on, kernel hardening. Individually small; together they *own* the shadow/stealth identity and answer the perennial "why is Linux not secure by default" complaint.
- **Impact ★★ · Effort E–M (stacked) · 🜂🜂**

---

## Tier 1 — Quick wins (high demand, mostly pure config → fits the current live-ISO model, no installer rework)

The "polish pass." Most are a config file in `/etc/skel` or `config/includes.chroot`. Could ship as **1.0.7** with low risk and a big perceived-quality jump.

| Idea | What | Impact | Effort |
|---|---|---|---|
| **Media codecs preinstalled** | gstreamer bad/ugly/libav + ffmpeg so MP3/MP4/HEVC just play. The **#1 switcher retention killer** ("installed it, couldn't play a video"). | ★★★ | E |
| **Flatpak + Flathub pre-enabled in Discover** | Modern, up-to-date app store on first boot — no terminal, no "is Flatpak safe?" research. #1 "completeness" signal. | ★★★ | E |
| **NVIDIA suspend/resume fix** | Pre-enable `nvidia-suspend/resume/hibernate.service` + `PreserveVideoMemoryAllocations=1`. Fixes the **#1 NVIDIA bug** (black screen after sleep). You already ship the driver. | ★★★ | E |
| **UFW on by default** (deny-in/allow-out) + GUFW GUI | Debian ships *no* active firewall. Easiest high-value security win on the list. | ★★ | E |
| **MAC randomization + IPv6 privacy** | Two NetworkManager drop-in files. Anti-tracking. 🜂 | ★★ | E |
| **Qt↔GTK dark bridging** | GTK/Flatpak apps inherit the Umbra dark theme (no blinding-white GIMP/Firefox). Perennial top-10 annoyance. | ★★ | E |
| **Font polish** | Slight hinting + subpixel in `/etc/fonts/local.conf`, **Inter** UI font + **JetBrainsMono Nerd Font**. "Linux fonts look bad" → fixed. | ★★ | E |
| **Bluetooth audio codecs** | WirePlumber config for LDAC/AptX + kill the SBC auto-downgrade. | ★★ | E |
| **auto-cpufreq** | Sane laptop battery life (Debian defaults can drain fast). | ★★ | E |
| **Nala** as apt frontend | Parallel downloads + `nala history undo`. Power-user love. | ★ | E |
| **Distrobox + Podman** | The escape hatch: run Arch/Fedora/AUR tools on stable Debian. Growing fast. | ★★ | E |
| **AppImage support** (`libfuse2`) | Vendor AppImages (Obsidian, Kdenlive) "just run." | ★ | E |
| **ZRAM compressed swap** | Free perf + no plaintext swap-to-disk. 🜂 | ★ | E |

---

## Tier 2 — The "real distro" milestone: a graphical installer

**Calamares graphical installer** (today Shadowfetch is a live ISO only). This is the biggest **ease-of-use** unlock and the *gateway* to several signature features. It brings: auto timezone/locale/keyboard, **dual-boot os-prober** ("I installed Linux and Windows is gone" → solved), guided partitioning, user creation — and critically lets us default to:
- **Btrfs + subvolume layout** → unlocks signature bet #2 (snapshots/rollback).
- **LUKS2 full-disk encryption as the default checkbox** → the #1 "Linux should encrypt by default" ask. 🜂

**Impact ★★★ · Effort M.** Calamares is packaged for Debian; the work is the `calamares-settings-shadowfetch` config + partitioning presets.

---

## Tier 3 — Cohesive "Umbra" visual identity (the premium feel)

Polished distros (Garuda/Nobara) share one visual language from power-on → login → desktop. Right now Umbra is the *desktop* theme; extend it to **own every moment.** Almost all pure assets + config drops.

> **🎨 Art direction LOCKED (2026-05-29)** — see `Shadowfetch Linux — Visual Motif Spec.md` (box: `branding/umbra-v2/UMBRA-THEME-SPEC.md`). Motif: *datacenter-forged graphite & gold* (cool ink-black + brushed gunmetal + warm gold glow + teal-steel shadow + signal-green terminal). **Accent = gold `#D8A24A`.** Tagline: *"Privacy, Power, and Precision from the Depths."* Wallpaper-grade frames, emblem sources, and the generated `Shadowfetch-Umbra` Plasma color scheme + Konsole scheme are all staged in `branding/umbra-v2/`. Caveat: emblem art is raster (AI-gen) — needs a clean **vector** redraw before the tiny (16–64px) logo slots.

- **Unified "Umbra" global look-and-feel** — Plasma theme + color scheme + window deco + SDDM + splash as one package. 🜂 **(the centerpiece)**
- **Custom GRUB theme** (Umbra-branded) — first thing users see.
- **Plymouth boot splash** — Umbra animation instead of a black screen.
- **Branded SDDM login** (Sugar Candy base, Umbra palette).
- **KWin blur/transparency** (`kwin-effects-forceblur`) + **floating panels** + **Panel Colorizer** — the frosted-glass r/unixporn look, pre-configured (Plasma 6 broke the old path; shipping it working is rare).
- **Papirus-Dark icons** + **Bibata cursor**.
- **Starship prompt + Nerd Fonts in `/etc/skel`** → Konsole opens beautiful on first boot. 🜂 (pairs with your existing modern-CLI set)
- **Tasteful KWin effects pre-enabled** (Magic Lamp, etc.).
- **Konsave "umbra" profile** so users can experiment and restore the default in one command.

**Impact ★★ · Effort E–M.** Could be **1.0.8 "Umbra Identity."**

---

## Tier 4 — Gaming stack (optional `shadowfetch-gaming` package set / spin)

Reddit is clear: a "gaming distro" needs the *full* stack, not Steam alone. Keep the heavy bits as first-boot downloads (ISO-size constraint).

- **Steam + Proton-GE** (via ProtonUp-Qt; Proton-GE pulled at first boot).
- **GameMode + MangoHud + Gamescope** — preconfigured with a dark MangoHud preset + launch aliases. (All in Debian repos — easy.)
- **Lutris + Heroic** (Epic/GOG/Amazon) as Flatpaks.
- **Controller udev rules** (DualSense/Xbox/Switch Pro/8BitDo work outside Steam).
- **NVIDIA PRIME/Optimus switching** + KDE right-click "Run with NVIDIA" (laptops).
- **vkBasalt** (sharpening), optional **linux-xanmod** perf kernel + `ananicy-cpp`.

**Impact ★★ (★★★ for the gaming segment) · Effort E–M.** Natural as a **separate "Arcade" spin** so the base stays lean.

---

## Tier 5 — Deep "Hardened" edition (advanced, very on-brand) 🜂

A power-user/privacy spin. Several are EASY config; a couple are real engineering.

- **LUKS2 + TPM2 auto-unlock** (with PIN) — FDE security, passwordless boot. (M)
- **Secure Boot w/ custom MOK + signed kernels/UKI** — completes the trust chain; **almost no Debian distro does this end-to-end.** (H, differentiator)
- **`security-misc`** (Kicksecure, Debian-compatible) — KSPP sysctls, disable unpriv userns, kptr_restrict, etc. (E)
- **AppArmor enforcing + Flatpak Wayland-only sandboxing.** (M)
- **Encrypted DNS** (dnscrypt-proxy DoH/DoQ + DNSSEC) + KDE tray indicator. (E–M) 🜂
- **VPN kill-switch** (NM dispatcher + UFW) + KDE toggle — pairs perfectly with the VPN GUIs you already ship. (M) 🜂
- **USBGuard + first-boot whitelist wizard** (BadUSB defense). (M)
- **Vorta + BorgBackup + first-boot backup wizard** — kills the "I'll back up later" failure mode; top "how do I" question. (E–M)
- **Amnesic / immutable live-mode toggle** (OverlayFS read-only root) — "boot clean, leave no trace." 🜂🜂 very on-brand. (M)
- **RAM wipe on shutdown** (cold-boot defense) + ZRAM. (E)
- **systemd-boot A/B kernel rollback** — alt to GRUB, auto-fallback on boot failure. (M)
- *sdwdate (Tor-based secure time) — niche, opt-in.*

---

## The glue: Welcome App v2 (`shadowfetch-welcome`)

Upgrade the existing welcome app into a **first-run action checklist** — the single most-cited "beginner friendly" feature and the natural one-click host for the bulky/optional items so they stay out of the ISO:
☑ Update system · ☑ Install media codecs · ☑ Driver manager (NVIDIA) · ☑ Take first snapshot · ☑ **Download an AI model** · ☑ Set up backups · ☑ Enable gaming stack · ☑ Docs + Discord/community link.

---

## Suggested sequencing

| Build | Theme | Contents | Risk |
|---|---|---|---|
| **1.0.7** | *Polish & Protect* | Tier 1 quick wins + Welcome-app v2 (codecs, Flathub, NVIDIA-resume, UFW, MAC, fonts, Bluetooth) | Low — mostly config, no installer change |
| **1.0.8** | *Umbra Identity* | Tier 3 cohesive theming (GRUB/Plymouth/SDDM/global theme/blur/Starship) | Low — assets + config |
| **1.1.0** | *Installed & Unbreakable* | Calamares installer + Btrfs subvolumes + auto-snapshots/rollback + LUKS2 FDE default | Med — the "real distro" leap |
| **1.2.0** | *Shadowfetch AI* 🜂 | Local Ollama + Open-WebUI, GPU-aware, localhost-hardened, first-boot model pull | Med — flagship |
| **1.3.0** | *Hardened* / *Arcade* | Tier 5 security spin and/or Tier 4 gaming spin as separate editions | Med |

**My recommendation:** do **1.0.7 "Polish & Protect"** next — it's almost all low-risk config, knocks out the highest-demand switcher complaints, and sets up the Welcome app that later hosts the AI/gaming one-click installs. Then make **"Shadowfetch AI" (1.2.0)** the headline release worth announcing.
