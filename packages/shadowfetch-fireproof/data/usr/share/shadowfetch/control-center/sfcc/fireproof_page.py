"""sfcc.fireproof_page -- Control Center adapter for the Fireproof Updates page.

The full FireproofPage widget lives in the standalone application script
/usr/bin/shadowfetch-fireproof (this package). The Control Center's Software &
Updates section imports `sfcc.fireproof_page.FireproofPage` (guarded, with a
built-in fallback card), so this thin module loads the script as a module and
re-exports the widget class. One implementation, two mounts, zero divergence.
"""
import importlib.machinery as _im
import importlib.util as _ilu

_SCRIPT = "/usr/bin/shadowfetch-fireproof"

# The script has no .py extension, so spec_from_file_location cannot infer a
# loader (returns None). Name the SourceFileLoader explicitly.
_loader = _im.SourceFileLoader("shadowfetch_fireproof_app", _SCRIPT)
_spec = _ilu.spec_from_loader("shadowfetch_fireproof_app", _loader)
if _spec is None:
    raise ImportError(f"cannot load {_SCRIPT}")
_mod = _ilu.module_from_spec(_spec)
_loader.exec_module(_mod)

FireproofPage = _mod.FireproofPage
