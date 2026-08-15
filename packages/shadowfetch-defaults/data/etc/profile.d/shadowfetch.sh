# Shadowfetch shell profile additions
# Sourced from /etc/profile for login shells.

# Bail if non-interactive
case $- in *i*) ;; *) return;; esac

alias ll='ls -lah --color=auto'
alias grep='grep --color=auto'
alias fetch='fastfetch'

# Print a fastfetch banner once per session, only on real terminals.
if [ -z "$SHADOWFETCH_FETCHED" ] && [ -t 1 ]; then
    export SHADOWFETCH_FETCHED=1
    command -v fastfetch >/dev/null 2>&1 && fastfetch
fi
