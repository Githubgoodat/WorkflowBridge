# Reproducible two-entry Windows bundle: one GUI and one JSON/stdio CLI.
from pathlib import Path

root = Path(SPECPATH).resolve().parent
hidden = ["tools.workflow_hook", "tools.workflow_event", "tools.workflow_question", "tools.prepare_codex_hooks", "qrcode"]
analysis = Analysis([str(root / "main.py")], pathex=[str(root)],
    binaries=[], datas=[], hiddenimports=hidden, hookspath=[], runtime_hooks=[],
    excludes=["aipet", "torch", "tensorflow", "numpy", "scipy", "pandas", "matplotlib", "PIL", "IPython", "pytest"],
    noarchive=False)
pyz = PYZ(analysis.pure)
gui = EXE(pyz, analysis.scripts, [], exclude_binaries=True, name="WorkflowBridge",
          console=False, debug=False, strip=False, upx=False)
cli = EXE(pyz, analysis.scripts, [], exclude_binaries=True, name="WorkflowBridge-CLI",
          console=True, debug=False, strip=False, upx=False)
bundle = COLLECT(gui, cli, analysis.binaries, analysis.datas,
                 strip=False, upx=False, name="WorkflowBridge")
