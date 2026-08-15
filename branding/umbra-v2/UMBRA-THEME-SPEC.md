# Shadowfetch Linux — "Umbra v2" Visual Motif Spec

*Derived 2026-05-29 from the 20 reference frames in `Shadowfetch Linux 20 New Photos/` (emblem set, server-room/datacenter scenes, website UI, device-suite mockups). Palette hexes were color-sampled from the source images, not eyeballed. This is the concrete art direction for the Tier-3 "Umbra Identity" build.*

## The one-line motif
**Datacenter-forged graphite & gold.** A brushed-metal emblem cradled by two stylized hands/wings around a warm glowing core (Tux in the light), set against cool ink-black server-room depth, with thin gold hairlines, PCB gold traces, and volumetric god-rays. Cool teal-steel shadows on one side, warm amber glow on the other; a signal-green "power LED" / terminal pop.

**Brand tagline (from the frames):** *"Privacy, Power, and Precision from the Depths."*

## Palette tokens (sampled from the references)

| Token | Hex | RGB | Use |
|---|---|---|---|
| **Umbra Ink** (base bg) | `#0A0D11` | 10,13,17 | desktop/base background (cool near-black) |
| **Abyss** (deep shadow) | `#05080B` | 5,8,11 | darkest panels, vignette |
| **Steel** (surface) | `#161A20` | 22,26,32 | panels, cards |
| **Steel Raised** | `#1E242B` | 30,36,43 | buttons, raised surfaces |
| **Slate** (border/inactive) | `#2C333B` | 44,51,59 | borders, dividers |
| **Graphite** (brushed metal) | `#4A4F56` | 74,79,86 | metal surfaces, inactive icons |
| **Mist** (secondary text) | `#9AA3AD` | 154,163,173 | secondary text, captions |
| **Text** (primary) | `#D6DBE1` | 214,219,225 | primary text |
| **★ Gold** (PRIMARY ACCENT / glow) | `#D8A24A` | 216,162,74 | accent: buttons, selection, links, KDE accent color |
| **Gold Bright** (highlight) | `#E8B65E` | 232,182,94 | hover/focus, cursor, glow highlight |
| **Gold Deep** | `#A6792F` | 166,121,47 | pressed, gold hairline shadow |
| **Teal Steel** (secondary accent) | `#4FA6B8` | 79,166,184 | cool secondary highlight, info |
| **Signal Green** (status/terminal) | `#34D058` | 52,208,88 | success, "power LED", terminal green |
| **Amber Warn** | `#E0A33A` | 224,163,58 | warnings |
| **Rack Red** (error) | `#E0484B` | 224,72,75 | errors, the red rack LEDs |

**Accent color for KDE Plasma 6: Gold `#D8A24A`.** The whole system reads graphite-dark with a single warm gold accent; teal-steel and signal-green are secondary pops only.

## Motif elements (the visual vocabulary)
1. **The plaque/tile** — a rounded-square beveled brushed-metal faceplate (reads like a premium device or app icon). Shape language for: app/menu icon, login avatar frame, "About" badge, widget corners.
2. **Cupped hands/wings around a glowing core** — the logo gesture ("fetch the light from the depths / hold it"). Tux penguin sits in the warm core.
3. **Warm radial glow / god-rays** — amber sunburst behind the core; lens flare; light shafts. The signature "light in the dark."
4. **Gold hairline frame** — a thin bronze/gold border around compositions.
5. **PCB gold traces** — circuit-board line work on dark as a background texture.
6. **Datacenter depth** — server racks with green/amber/red/blue LED bokeh, cable runs, shallow DoF, volumetric haze. The "from the depths" backdrop.
7. **Moods** (per the manifest): `teal_gold` (hero), `graphite` (mono brushed metal), `cold` (desaturated blue-gray), `warm` (gold/bronze), `terminal` (green-on-metal).

## How it maps to the distro (Tier-3 "Umbra Identity")
| Distro component | Treatment | Source asset |
|---|---|---|
| **Default wallpaper set** | graphite + datacenter + server-room scenes | `02`, `10`, `06` (2560×1440); `09`,`17` (ultrawide 3200×1060); `11`,`20` (banners) |
| **Lock/login (SDDM)** | blurred datacenter scene + gold accents + emblem | `03` (1440×2560 portrait), `10`/`06` |
| **Plasma color scheme** | "Shadowfetch Umbra" — graphite dark, **gold accent** | → `Shadowfetch-Umbra.colors` (generated) |
| **Accent color** | Gold `#D8A24A` | — |
| **Konsole / terminal** | graphite bg, green+gold+teal ANSI, gold cursor | → `Shadowfetch-Umbra.colorscheme` (generated) |
| **GRUB theme** | ink-black bg, emblem, gold-highlighted selection | `01`/`04` emblem |
| **Plymouth boot splash** | black → warm glow pulse reveal behind emblem (god-ray) | emblem |
| **App-menu / panel logo** | the plaque emblem | `01`/`04` (see caveat) |
| **fastfetch/neofetch logo** | emblem (image) or gold ASCII "SF" | — |
| **os-release / branding** | LOGO + tagline | — |

## Caveats / to-source
- The emblem frames are **AI-generated raster** with slight detail variance between images and a small 4-point **sparkle watermark** in a corner (Gemini artifact). They're perfect for **wallpapers, splash, large hero logo**. For **crisp tiny sizes** (16–64px panel icon, GRUB, favicon) we want a **clean redrawn vector (SVG)** of the hands+core+SF+Tux mark. → Action: produce a vector emblem (or commission one) before wiring the small-size logo slots.
- Keep the gold accent *restrained* — one accent, lots of graphite. The references work because the gold is a glow, not a flood.
