"""sfcc - Shadowfetch Control Center modules (2.1.2 "Fire Edition").

The Control Center executable at /usr/bin/shadowfetch-control is a thin
front door: it answers --help/--version before any Qt import, handles the
terminal fallback, then hands over to sfcc.app.run().  Everything visual
lives here, one module per sidebar section, all drawing from sfcc.theme so
the six sections read as one application.

Nothing in this package talks to the network.  Every number shown in the
UI comes from a local D-Bus service (org.shadowfetch.Firewatch1,
com.shadowfetch.Ember1, org.opensuse.Snapper, org.shadowfetch.Fireproof1),
a local fact file (/var/lib/shadowfetch/hwscan.json), or a local command.
When a source is unavailable the page says so in plain words instead of
showing stale or invented numbers.
"""

__all__ = [
    "app",
    "busutil",
    "theme",
    "ember_page",
    "firewatch_page",
    "phoenix_page",
    "agents_page",
    "drivers_page",
    "software_page",
]
