from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent
    command = [sys.executable, str(project_root / "main.py")]
    subprocess.Popen(command, cwd=project_root)
    subprocess.Popen(command, cwd=project_root)
    print("Se abrieron dos instancias de SecureDesk para tu demo.")


if __name__ == "__main__":
    main()
