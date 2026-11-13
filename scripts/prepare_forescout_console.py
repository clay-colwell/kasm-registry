#!/usr/bin/env python3
"""Normalize a vendor Linux installer to the archive consumed by the image build."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import uuid

from generate_forescout_workspaces import source_version, validate_archive

# Pin the multi-platform Debian manifest; the vendor installer requires amd64.
INSTALLER_IMAGE = "debian:12-slim@sha256:734a72b3d6142a71993b4bc580ca01d8ca687f77a2c422d96a961d3376b179bc"
INSTALL_SCRIPT = r'''
set -eu
export HOME=/home/kasm-user
mkdir -p "$HOME"
cp /input/setup.run /tmp/setup.run
chmod 0755 /tmp/setup.run
timeout 600 /tmp/setup.run --mode unattended --unattendedmodeui none --prefix "$HOME/Forescout Console"
console="$HOME/Forescout Console"
current="$console/GuiManager/current"
test -x "$current/Forescout Console"
version_file="$current/etc/version.properties"
if [ -f "$console/etc/version.properties" ]; then version_file="$console/etc/version.properties"; fi
actual=$(sed -n 's/^version=//p' "$version_file" | tr -d '\r')
if [ "$actual" != "$1" ]; then
    echo "Installer version mismatch: expected $1, installed $actual" >&2
    exit 1
fi
java=$(sed -n 's/^preferred_java_binary=//p' "$current/Forescout Console.properties" | tr -d '\r')
case "$java" in ../../jre*/bin/java) ;; *) echo "Unexpected Java path: $java" >&2; exit 1;; esac
test -x "$current/$java"
# Verify the bundled runtime can execute in Linux without starting the GUI.
"$current/$java" -version
: > "$current/etc/local.properties"
: > "$current/etc/login.fingerprint.properties"
tar -C "$HOME" -czf /output/console.tar.gz 'Forescout Console'
'''


def prepare(source, output=None):
    source = source.resolve()
    version = source_version(source.name)
    if not source.is_file():
        raise SystemExit(f"Console source not found: {source}")
    if source.name.endswith('.tar.gz'):
        validate_archive(source)
        return source
    with source.open('rb') as stream:
        if stream.read(4) != b'\x7fELF':
            raise SystemExit(f"Expected a Linux ELF installer (check Git LFS download): {source}")
    output = (output or source.parent / '.prepared' / f'{version}.tar.gz').resolve()
    if output.exists():
        raise SystemExit(f"Output already exists; remove it before converting again: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='forescout-', dir=output.parent) as temporary:
        container_name = f"forescout-prepare-{uuid.uuid4().hex}"
        try:
            subprocess.run([
                'docker', 'run', '--rm', '--name', container_name,
                '--platform', 'linux/amd64', '--network', 'none',
                '--user', f'{os.getuid()}:{os.getgid()}', '--cap-drop', 'ALL',
                '--security-opt', 'no-new-privileges', '--tmpfs', '/home:mode=1777,exec',
                '-v', f'{source}:/input/setup.run:ro', '-v', f'{temporary}:/output',
                INSTALLER_IMAGE, '/bin/sh', '-c', INSTALL_SCRIPT, 'prepare-console', version,
            ], check=True, timeout=900)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            # Stopping the Docker client alone would leave its container running.
            subprocess.run(['docker', 'rm', '-f', container_name], check=False)
            raise
        archive = Path(temporary) / 'console.tar.gz'
        validate_archive(archive)
        archive.replace(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, help='optional output archive path for .run input')
    args = parser.parse_args()
    try:
        print(prepare(args.source, args.output))
    except (OSError, subprocess.SubprocessError) as error:
        raise SystemExit(f"Console conversion failed: {error}") from None


if __name__ == '__main__':
    main()
