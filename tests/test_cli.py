import subprocess
import sys


def test_software_engineer_cli() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "software_engineer", "World"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "Hello, World! (development)"
