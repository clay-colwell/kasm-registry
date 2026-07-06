#!/usr/bin/env bash
set -euo pipefail

CONSOLE_HOME="/home/kasm-user/Forescout Console"
CURRENT_DIR="$CONSOLE_HOME/GuiManager/current"
VERSION_FILE="$CONSOLE_HOME/etc/version.properties"
DOWNLOADS_DIR="/home/kasm-user/Downloads"
CONSOLE_PROCESS="$CURRENT_DIR/Forescout Console"

if pgrep -f -- "$CONSOLE_PROCESS" >/dev/null 2>&1; then
    echo "Forescout Console is currently running."
    echo "This script cannot run while the Console is running. Please close it and try again."
    exit 1
fi

cat <<'EOF'
This utility modifies the installed Forescout Console before packaging it.

It is strongly recommended that you run it in a Kasm session that does NOT
have Persistent Profile enabled. Running it against a persistent profile will
permanently clean the Console directory stored in that profile.
EOF

while true; do
    printf '\nAre you running without Persistent Profile?\n'
    printf '  1) Yes, continue (recommended)\n'
    printf '  2) No, stop and exit\n'
    printf '  3) Override and continue with Persistent Profile enabled\n'
    read -r -p 'Select [1-3]: ' response
    case "$response" in
        1|yes|YES|y|Y)
            break
            ;;
        2|no|NO|n|N)
            echo "No changes were made."
            exit 0
            ;;
        3|override|OVERRIDE)
            echo "Override accepted. Continuing with the persistent-profile warning acknowledged."
            break
            ;;
        *)
            echo "Please select 1, 2, or 3."
            ;;
    esac
done

if [[ ! -d "$CURRENT_DIR" ]]; then
    echo "Forescout Console directory not found: $CURRENT_DIR" >&2
    exit 1
fi

if [[ ! -f "$VERSION_FILE" && -f "$CURRENT_DIR/etc/version.properties" ]]; then
    VERSION_FILE="$CURRENT_DIR/etc/version.properties"
fi

if [[ ! -f "$VERSION_FILE" ]]; then
    echo "Version file not found: $VERSION_FILE" >&2
    exit 1
fi

version=$(awk -F= '$1 == "version" { sub(/\r$/, "", $2); print $2; exit }' "$VERSION_FILE")
if [[ ! "$version" =~ ^[0-9]+([.][0-9]+)*$ ]]; then
    echo "Could not read a valid version from $VERSION_FILE" >&2
    exit 1
fi

echo "Preparing Forescout Console $version..."

: > "$CURRENT_DIR/etc/login.fingerprint.properties"
: > "$CURRENT_DIR/etc/local.properties"

find "$CURRENT_DIR" -maxdepth 1 -name 'connect_connect_*' -exec rm -rf -- {} +
find "$CURRENT_DIR" -maxdepth 1 -name 'pluginsetup*' -exec rm -rf -- {} +

for directory in tmp plugin modules log reports; do
    if [[ -d "$CURRENT_DIR/$directory" ]]; then
        find "$CURRENT_DIR/$directory" -mindepth 1 -delete
    fi
done

mkdir -p "$DOWNLOADS_DIR"
archive="$DOWNLOADS_DIR/$version.tar.gz"
temporary_archive="$DOWNLOADS_DIR/.$version.tar.gz.tmp.$$"
trap 'rm -f -- "$temporary_archive"' EXIT

tar -C /home/kasm-user -czf "$temporary_archive" "Forescout Console"
tar -tzf "$temporary_archive" "Forescout Console" >/dev/null
mv -f -- "$temporary_archive" "$archive"
trap - EXIT

echo "Package created successfully: $archive"
echo "Upload this archive to workspaces/Forescout Console/console/ in the registry repository."
