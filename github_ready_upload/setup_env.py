"""Create a local virtual environment and install the project dependencies."""

from pathlib import Path
import subprocess
import sys
import venv


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Please install Python 3.10 or newer, then run setup again.")
    root = Path(__file__).resolve().parent
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not python.exists():
        print("Creating .venv for this computer...", flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    print("Installing the project requirements...", flush=True)
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(root / "requirements.txt")],
                   cwd=root, check=True)
    print("\nSetup complete.")
    print("Run the simulation:", python, "simulation.py")
    print("Run the tests:", python, "-m unittest -v")


if __name__ == "__main__":
    main()
