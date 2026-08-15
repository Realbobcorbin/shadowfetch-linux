#!/bin/sh
# Shadowfetch first-boot setup - idempotent, safe to run on every boot.
STAMP=/var/lib/shadowfetch/firstboot.done
[ -f "$STAMP" ] && exit 0
mkdir -p /var/lib/shadowfetch

# Flathub remote (offline from shipped repo file)
if command -v flatpak >/dev/null 2>&1; then
    if [ -f /usr/share/shadowfetch/flathub.flatpakrepo ]; then
        flatpak remote-add --if-not-exists flathub /usr/share/shadowfetch/flathub.flatpakrepo 2>/dev/null
    else
        flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null
    fi
fi

# Flatpak theming: make Flatpak apps match the dark desktop (best-effort, needs network)
if command -v flatpak >/dev/null 2>&1; then
    flatpak install -y --noninteractive flathub org.gtk.Gtk3theme.adw-gtk3 org.gtk.Gtk3theme.adw-gtk3-dark >/dev/null 2>&1 || true
    flatpak override --env=GTK_THEME=adw-gtk3-dark 2>/dev/null || true
    flatpak override --env=ICON_THEME=Papirus-Dark 2>/dev/null || true
fi

# Keep the hardware clock in UTC and correct drift as soon as networking is ready.
timedatectl set-local-rtc 0 --adjust-system-clock 2>/dev/null || true
systemctl enable --now systemd-timesyncd.service 2>/dev/null || true

# Firewall: defaults + open ports our shipped apps need
if command -v ufw >/dev/null 2>&1; then
    ufw --force default deny incoming 2>/dev/null
    ufw --force default allow outgoing 2>/dev/null
    ufw limit OpenSSH 2>/dev/null || ufw limit 22/tcp 2>/dev/null
    ufw allow 1714:1764/udp 2>/dev/null
    ufw allow 1714:1764/tcp 2>/dev/null
    ufw allow 5353/udp 2>/dev/null
    ufw --force enable 2>/dev/null
fi

# Enable QoL services (idempotent; most auto-enable via preset)
for s in cups cups-browsed avahi-daemon ipp-usb earlyoom irqbalance fstrim.timer flatpak-system-update.timer rfkill-unblock.service shadowfetch-regdomain.service; do
    systemctl enable --now "$s" 2>/dev/null
done

# thermald: Intel only
if grep -qi GenuineIntel /proc/cpuinfo 2>/dev/null; then
    systemctl enable --now thermald 2>/dev/null
fi

# NVIDIA suspend/resume services if the driver shipped them
for s in nvidia-suspend nvidia-resume nvidia-hibernate; do
    if [ -f "/lib/systemd/system/$s.service" ] || [ -f "/usr/lib/systemd/system/$s.service" ]; then
        systemctl enable "$s.service" 2>/dev/null
    fi
done

# --- Snapshots & rollback (1.2.9): configure snapper + grub-btrfs when root is Btrfs ---
if command -v snapper >/dev/null 2>&1 && [ "$(stat -f -c %T / 2>/dev/null)" = "btrfs" ]; then
    if [ ! -f /etc/snapper/configs/root ]; then
        snapper -c root create-config / 2>/dev/null
        if [ -f /etc/snapper/configs/root ]; then
            snapper -c root set-config TIMELINE_CREATE=yes TIMELINE_CLEANUP=yes NUMBER_CLEANUP=yes NUMBER_MIN_AGE=1800 NUMBER_LIMIT=12 NUMBER_LIMIT_IMPORTANT=6 TIMELINE_LIMIT_HOURLY=6 TIMELINE_LIMIT_DAILY=5 TIMELINE_LIMIT_WEEKLY=2 TIMELINE_LIMIT_MONTHLY=0 TIMELINE_LIMIT_YEARLY=0 2>/dev/null
            primary=$(getent passwd 1000 | cut -d: -f1)
            [ -n "$primary" ] && snapper -c root set-config ALLOW_USERS="$primary" SYNC_ACL=yes 2>/dev/null
        fi
    fi
    systemctl enable --now snapper-timeline.timer snapper-cleanup.timer 2>/dev/null
    # 2.0.0 Bedrock: boot-to-snapshot. grub-btrfsd watches .snapshots and
    # regenerates the GRUB submenu so any snapshot is bootable from the menu.
    if command -v grub-btrfsd >/dev/null 2>&1; then
        systemctl enable --now grub-btrfsd 2>/dev/null || systemctl enable --now grub-btrfsd.service 2>/dev/null || true
    fi
    if command -v update-grub >/dev/null 2>&1; then update-grub 2>/dev/null || true; fi

fi


# Debian ships these under renamed binaries; add the names users expect (bat, fd)
mkdir -p /usr/local/bin
[ -x /usr/bin/batcat ] && ln -sf /usr/bin/batcat /usr/local/bin/bat 2>/dev/null
[ -x /usr/bin/fdfind ] && ln -sf /usr/bin/fdfind /usr/local/bin/fd 2>/dev/null

touch "$STAMP"
exit 0
