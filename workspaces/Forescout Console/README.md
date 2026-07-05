# Forescout Console Kasm workspace

Add each Linux Forescout Console bundle to `console/` as `<version>.tar.gz`, for
example `8.5.5.tar.gz` or `9.1.6.tar.gz`. The archive must contain one top-level
folder named `Forescout Console`. Console archives use Git LFS because they can
exceed GitHub's normal 100 MB file limit.

On a matching push, GitHub Actions:

1. validates every archive and generates one registry workspace per version;
2. builds an amd64 image for each Kasm/base-image combination;
3. publishes explicit tags such as `8.5.5-kasm-1.19.0` to
   `ghcr.io/clay-colwell/forescout-console`; and
4. commits the generated workspace metadata, which triggers the existing
   registry site deployment.

The same workflow checks the upstream rolling-weekly images every Monday at
03:00 America/New_York. It compares the current base manifest digest with the
digest recorded on the published image and skips unchanged combinations.

The repository must allow GitHub Actions to read/write repository contents and
packages. Make the GHCR package public if Kasm should pull it without registry
credentials; otherwise configure GHCR credentials in Kasm.

To regenerate metadata locally:

```bash
python3 scripts/generate_forescout_workspaces.py
```
