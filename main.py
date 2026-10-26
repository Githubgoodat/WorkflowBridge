"""GUI entry and console-compatible workflow producer commands."""
from __future__ import annotations
import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        configure = getattr(stream, "reconfigure", None)
        if callable(configure):
            configure(encoding="utf-8", errors="backslashreplace")
    commands = {"--question": "workflow_question", "--event": "workflow_event", "--hook": "workflow_hook",
                "--prepare-hooks": "prepare_codex_hooks"}
    if args and args[0] in commands:
        from importlib import import_module
        return import_module("tools." + commands[args[0]]).main(args[1:])
    from workflow_bridge.application import main as gui_main
    return gui_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
