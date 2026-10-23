#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
from pathlib import Path

studio_dir = Path(__file__).resolve().parent
apps_dir = studio_dir.parent
venv_py = apps_dir / "Transcriptor" / "entorno" / "Scripts" / "python.exe"
python_exec = str(venv_py) if venv_py.exists() else sys.executable

cmd = [
    python_exec,
    "-m", "PyInstaller",
    "--noconsole",
    "--name", "OmniVideo Studio",
    "--icon", str(studio_dir / "iconos" / "omnisuite.ico"),
    "--add-data", f"{studio_dir / 'iconos'};iconos",
    "--add-data", f"{apps_dir / 'ui_theme.py'};.",
    "--add-data", f"{apps_dir / 'omni_core'};omni_core",
    "--distpath", str(studio_dir / "dist"),
    "--workpath", str(studio_dir / "build"),
    "--noconfirm",
    str(studio_dir / "app_omnivideo_studio.py")
]

print("Compilando OmniVideo Studio.exe con PyInstaller...")
res = subprocess.run(cmd, cwd=str(studio_dir))
if res.returncode == 0:
    print("[OK] PyInstaller completado exitosamente!")
else:
    print("[ERROR] Falló la compilación con PyInstaller.")
    sys.exit(res.returncode)
