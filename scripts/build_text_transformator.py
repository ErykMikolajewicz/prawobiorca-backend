import subprocess
from pathlib import Path

text_transformator_path = Path('text_transformator')

cmd = ['podman',
       'image',
       'build',
       '--tag=text_transformator',
       '.']

if __name__ == '__main__':
    subprocess.run(cmd, shell=True, cwd=text_transformator_path)