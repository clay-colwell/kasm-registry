# Bruno

This workspace installs the current amd64 Bruno desktop package from Bruno's
APT repository on top of
`kasmweb/core-ubuntu-jammy:1.19.0-rolling-weekly` and launches Bruno when the
Kasm desktop is ready.

The registry icon is extracted from the Bruno Debian package. Bruno's project
README attributes its logo to OpenMoji under CC BY-SA 4.0.

## Local build

Resolve the current base digest, then build from the repository root:

```bash
BASE_IMAGE=kasmweb/core-ubuntu-jammy:1.19.0-rolling-weekly
BASE_DIGEST=$(docker buildx imagetools inspect "$BASE_IMAGE" --format '{{.Manifest.Digest}}')

docker build \
  --build-arg "BASE_IMAGE=$BASE_IMAGE" \
  --build-arg "BASE_DIGEST=$BASE_DIGEST" \
  -t ghcr.io/clay-colwell/bruno:1.19.0-rolling-weekly \
  workspaces/Bruno
```
