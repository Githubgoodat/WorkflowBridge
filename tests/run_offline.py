"""Test independent sources against fixtures; block network and subprocesses."""
from pathlib import Path
import json
import os
import sys
import tempfile
import time
import unittest


def audit(event, _arguments):
    if event in {"socket.connect", "socket.connect_ex", "socket.bind", "socket.getaddrinfo",
                 "socket.gethostbyname", "socket.gethostbyaddr", "subprocess.Popen", "os.system",
                 "os.posix_spawn", "os.posix_spawnp"}:
        raise RuntimeError("Standalone offline tests forbid external network and processes: " + event)


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    sys.dont_write_bytecode = True
    os.chdir(root)
    with tempfile.TemporaryDirectory(prefix="workflow-bridge-tests-") as temporary:
        os.environ["WORKFLOW_BRIDGE_HOME"] = str(Path(temporary) / "isolated-data")
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        sys.addaudithook(audit)
        started = time.monotonic()
        suite = unittest.defaultTestLoader.discover(str(root / "tests"), top_level_dir=str(root))
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        print(json.dumps({"scope":"standalone offline regression", "tests_run":result.testsRun,
            "passed":result.testsRun-len(result.errors)-len(result.failures)-len(result.skipped),
            "errors":len(result.errors), "failures":len(result.failures), "skipped":len(result.skipped),
            "seconds":round(time.monotonic()-started, 2), "external_services_used":False}))
        return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
