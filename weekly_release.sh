#!/bin/bash
# Shadowfetch Linux — unattended weekly release with self-QA gating.
# Build -> verify (squashfs + kernel/initrd + ISO + sha256) -> publish ONLY if QA passes.
# Scoped passwordless sudo (lb/grub-mkrescue/chown/chmod) lets this run from cron.
set -uo pipefail
ROOT="$HOME/projects/shadowfetch"
LOG="$ROOT/weekly-release-$(date +%Y%m%d).log"
ROOM="1510771977579790346"   # brandy-elaine discord room
cd "$ROOT" || exit 1

# --- creds for publish (R2 S3 API) from elaine's env ---
set -a; [ -f "$HOME/.hermes/profiles/elaine/.env" ] && . "$HOME/.hermes/profiles/elaine/.env"; set +a
# Map R2 creds to AWS vars the Makefile expects (only if provided under R2_* names)
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-${R2_ACCESS_KEY_ID:-}}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-${R2_SECRET_ACCESS_KEY:-}}"

notify(){ # post a short line to brandy-elaine via brandy admin token
  local msg="$1"
  local tok=$(grep -m1 '^DISCORD_BOT_TOKEN=' "$HOME/.hermes/profiles/brandy/.env" | cut -d= -f2- | tr -d '"'"'"' ')
  [ -z "$tok" ] && return 0
  curl -s -X POST "https://discord.com/api/v10/channels/$ROOM/messages" \
    -H "Authorization: Bot $tok" -H "User-Agent: DiscordBot (https://shadowfetch.com, 1.0)" \
    -H "Content-Type: application/json" \
    --data "$(python3 -c 'import json,sys;print(json.dumps({"content":sys.argv[1][:1900]}))' "$msg")" >/dev/null 2>&1
}

# --- version bump: read current VERSION from Makefile, bump patch ---
CUR=$(grep -m1 '^VERSION' Makefile | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
IFS=. read -r MA MI PA <<< "$CUR"; NEW="$MA.$MI.$((PA+1))"
ISO="shadowfetch-$NEW-amd64.iso"
echo "=== weekly release $(date) : $CUR -> $NEW ===" | tee -a "$LOG"
notify "🛠️ Weekly Linux build starting: $CUR → $NEW. I'll report when it's built + QA'd."

# --- build (packages -> repo -> iso), all logged ---
if ! make VERSION="$NEW" iso >>"$LOG" 2>&1; then
  notify "🔴 HOLD $NEW: \`make iso\` FAILED. No publish. Check $LOG on the box."
  echo "BUILD_FAILED"; exit 1
fi

# --- self-QA gate: artifacts must exist + be sane ---
SQUASH="$ROOT/live-build/binary/live/filesystem.squashfs"
fail=""
[ -f "$ROOT/$ISO" ] || fail="$fail no-ISO"
[ -f "$SQUASH" ] || fail="$fail no-squashfs"
[ -f "$ROOT/$ISO.sha256" ] || fail="$fail no-sha256"
[ -f "$ROOT/$ISO.asc" ] || fail="$fail no-signature"
# ISO must be a believable size (>700MB)
if [ -f "$ROOT/$ISO" ]; then
  sz=$(stat -c%s "$ROOT/$ISO"); [ "$sz" -lt 734003200 ] && fail="$fail iso-too-small($sz)"
fi
# sha256 must verify
if [ -f "$ROOT/$ISO.sha256" ]; then sha256sum -c "$ROOT/$ISO.sha256" >>"$LOG" 2>&1 || fail="$fail sha-mismatch"; fi
if [ -n "$fail" ]; then
  notify "🔴 HOLD $NEW: built but QA FAILED ($fail). NOT publishing. Log: $LOG"
  echo "QA_FAILED:$fail"; exit 1
fi
SZ=$(du -h "$ROOT/$ISO" | cut -f1)
echo "QA_PASS iso=$ISO size=$SZ" | tee -a "$LOG"

# --- pre-release publication gate: apt Valid-Until + repo hygiene ---
if ! make VERSION="$NEW" pre-release-check >>"$LOG" 2>&1; then
  notify "🔴 HOLD $NEW: pre-release publication gate FAILED. No publish. Check $LOG on the box."
  echo "PRE_RELEASE_CHECK_FAILED"; exit 1
fi

# --- publish (R2: ISO + sha + sig + APT repo) ---
if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
  notify "🟡 $NEW BUILT + QA PASSED ($SZ) but R2 publish creds missing on box — couldn't auto-upload. ISO is ready at ~/projects/shadowfetch/$ISO. Add R2_ACCESS_KEY_ID/R2_SECRET_ACCESS_KEY to elaine/.env to enable auto-publish."
  echo "PUBLISH_SKIPPED_NO_CREDS"; exit 0
fi
if make VERSION="$NEW" publish >>"$LOG" 2>&1; then
  notify "🟢 SHIPPED Shadowfetch Linux $NEW ($SZ) — ISO + APT repo live on R2. Verify: https://shadowfetch.com/linux/  · Note: Worker (\`make deploy-worker\`) runs Mac-side if the download page needs the new version wired."
  echo "PUBLISHED $NEW"
else
  notify "🔴 $NEW built+QA'd but PUBLISH failed (R2 upload). ISO is safe on box. Log: $LOG"
  echo "PUBLISH_FAILED"; exit 1
fi
