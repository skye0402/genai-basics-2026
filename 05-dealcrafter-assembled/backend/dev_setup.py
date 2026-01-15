import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _venv_python(backend_dir: Path) -> Path:
    if platform.system().lower().startswith("win"):
        return backend_dir / ".venv" / "Scripts" / "python.exe"
    return backend_dir / ".venv" / "bin" / "python"


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev_setup.py",
        description=(
            "Cross-platform dev setup for DealCrafter backend: sync dependencies, install extra libs, and optionally start the server."
        ),
    )
    parser.add_argument(
        "--install",
        action="append",
        default=[],
        help="Additional package to install into the environment (repeatable). Example: --install deepagents",
    )
    parser.add_argument(
        "--skip-sync",
        action="store_true",
        help="Skip 'uv sync'.",
    )
    parser.add_argument(
        "--start-server",
        action="store_true",
        help="Start backend server at the end using .venv's python (python app/main.py).",
    )

    args = parser.parse_args()

    backend_dir = Path(__file__).resolve().parent

    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError(
            "'uv' was not found on PATH. Install uv first: https://docs.astral.sh/uv/"
        )

    if not args.skip_sync:
        _run([uv, "sync"], cwd=backend_dir)

    for pkg in args.install:
        _run([uv, "pip", "install", pkg], cwd=backend_dir)

    venv_py = _venv_python(backend_dir)
    if args.start_server:
        if not venv_py.exists():
            raise RuntimeError(
                f"Expected venv python at '{venv_py}', but it does not exist. Run with --skip-sync=false to create/sync the .venv first."
            )
        os.execv(str(venv_py), [str(venv_py), "app/main.py"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
