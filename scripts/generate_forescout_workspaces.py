#!/usr/bin/env python3
"""Generate registry metadata and a GitHub Actions build matrix."""

import argparse
import json
import re
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT / "workspaces" / "Forescout Console"
CONSOLE_ROOT = WORKSPACE_ROOT / "console"
GENERATED_ROOT = WORKSPACE_ROOT / "generated"
VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")


def load_config():
    with (WORKSPACE_ROOT / "image-config.json").open(encoding="utf-8") as stream:
        return json.load(stream)


def archives():
    found = []
    for archive in sorted(CONSOLE_ROOT.glob("*.tar.gz")):
        version = archive.name[:-7]
        if not VERSION_RE.fullmatch(version):
            raise SystemExit(f"Invalid console archive name: {archive.name}")
        validate_archive(archive)
        found.append((version, archive.name))
    return found


def validate_archive(archive):
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        if not members:
            raise SystemExit(f"Empty console archive: {archive.name}")
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise SystemExit(f"Unsafe path in {archive.name}: {member.name}")
            if not path.parts or path.parts[0] != "Forescout Console":
                raise SystemExit(
                    f'{archive.name} must contain only a top-level "Forescout Console" folder'
                )


def image_name(config, console_version):
    return f"{config['image_prefix']}{console_version}"


def image_tag(kasm_version):
    return f"{kasm_version}-rolling-weekly"


def build_matrix(config):
    return {
        "include": [
            {
                "console_version": console_version,
                "console_archive": archive,
                "kasm_version": item["version"],
                "base_image": item["base"],
                "image": image_name(config, console_version),
                "tag": image_tag(item["version"]),
            }
            for console_version, archive in archives()
            for item in config["kasm_versions"]
        ]
    }


def generate(config):
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    expected = set()
    for console_version, _archive in archives():
        destination = GENERATED_ROOT / console_version
        expected.add(destination)
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(WORKSPACE_ROOT / "Icon.png", destination / "Icon.png")
        workspace_path = destination / "workspace.json"
        existing_sizes = {}
        if workspace_path.exists():
            with workspace_path.open(encoding="utf-8") as stream:
                existing = json.load(stream)
            existing_sizes = {
                item["image"]: item.get("uncompressed_size_mb", 0)
                for item in existing.get("compatibility", [])
            }
        compatibility = [
            {
                "version": item["version"],
                "image": f"{image_name(config, console_version)}:{image_tag(item['version'])}",
                "uncompressed_size_mb": existing_sizes.get(
                    f"{image_name(config, console_version)}:{image_tag(item['version'])}",
                    0,
                ),
            }
            for item in config["kasm_versions"]
        ]
        workspace = {
            "description": (
                f"Forescout Console ({console_version}), packaged for Kasm Workspaces. "
                "Select the compatibility entry matching your Kasm deployment."
            ),
            "docker_registry": "https://ghcr.io",
            "image_src": "Icon.png",
            "categories": ["Network Security", "Cyber Security"],
            "friendly_name": f"Forescout Console ({console_version})",
            "architecture": ["amd64"],
            "cores": 4,
            "memory": 4096,
            "compatibility": compatibility,
        }
        with workspace_path.open("w", encoding="utf-8") as stream:
            json.dump(workspace, stream, indent=2)
            stream.write("\n")

    for path in GENERATED_ROOT.iterdir():
        if path.is_dir() and path not in expected:
            shutil.rmtree(path)


def update_sizes(sizes_dir):
    sizes = {}
    for record_path in sizes_dir.glob("*.json"):
        with record_path.open(encoding="utf-8") as stream:
            record = json.load(stream)
        sizes[record["image"]] = record["uncompressed_size_mb"]

    if not sizes:
        raise SystemExit(f"No image-size records found in {sizes_dir}")

    updated = set()
    for workspace_path in GENERATED_ROOT.glob("*/workspace.json"):
        with workspace_path.open(encoding="utf-8") as stream:
            workspace = json.load(stream)
        for item in workspace.get("compatibility", []):
            if item["image"] in sizes:
                item["uncompressed_size_mb"] = sizes[item["image"]]
                updated.add(item["image"])
        with workspace_path.open("w", encoding="utf-8") as stream:
            json.dump(workspace, stream, indent=2)
            stream.write("\n")

    missing = set(sizes) - updated
    if missing:
        raise SystemExit(f"No workspace entries found for: {', '.join(sorted(missing))}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--matrix", action="store_true", help="print the Actions matrix only"
    )
    parser.add_argument(
        "--sizes-dir", type=Path, help="apply downloaded image-size records"
    )
    args = parser.parse_args()
    config = load_config()
    if args.sizes_dir:
        update_sizes(args.sizes_dir)
    elif args.matrix:
        print(json.dumps(build_matrix(config), separators=(",", ":")))
    else:
        generate(config)


if __name__ == "__main__":
    main()
