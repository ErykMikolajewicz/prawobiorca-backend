import subprocess

from local_manifests import MANIFESTS


def main():
    for manifest, _ in reversed(MANIFESTS):
        print(f"Removing {manifest.name}...")
        subprocess.run(["podman", "kube", "play", "--down", str(manifest)], check=False)

    print("\nLocal deployment stopped.")


if __name__ == "__main__":
    main()
