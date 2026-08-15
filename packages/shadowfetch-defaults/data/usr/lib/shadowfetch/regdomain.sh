#!/bin/sh
# Set the wireless regulatory domain from the system locale so 5/6 GHz channels
# unlock (vs the restrictive world '00' default). Best-effort; silent if no country.
CC=$(. /etc/default/locale 2>/dev/null; echo "${LANG:-${LC_ALL:-}}" | sed -n 's/.*_\([A-Z][A-Z]\).*/\1/p')
[ -n "$CC" ] && command -v iw >/dev/null 2>&1 && iw reg set "$CC" 2>/dev/null
exit 0
