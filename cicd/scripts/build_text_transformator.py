import subprocess
from pathlib import Path

text_transformator_path = Path("text-transformator")

cmd = ["podman", "image", "build", "--tag=text-transformator", "."]

if __name__ == "__main__":
    subprocess.run(cmd, cwd=text_transformator_path)
