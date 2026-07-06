#!/usr/bin/env bash
set -euo pipefail

CONSOLE_HOME="/home/kasm-user/Forescout Console"
GUI_MANAGER_DIR="$CONSOLE_HOME/GuiManager"
CURRENT_DIR="$GUI_MANAGER_DIR/current"
ETC_DIR="$CURRENT_DIR/etc"
VERSION_FILE="$CONSOLE_HOME/etc/version.properties"
CONSOLE_PROPERTIES="$CURRENT_DIR/Forescout Console.properties"
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

if [[ ! -f "$CONSOLE_PROPERTIES" ]]; then
    echo "Console properties file not found: $CONSOLE_PROPERTIES" >&2
    exit 1
fi

preferred_java_binary=$(awk -F= '
    $1 == "preferred_java_binary" {
        value = substr($0, index($0, "=") + 1)
        sub(/\r$/, "", value)
        print value
        exit
    }
' "$CONSOLE_PROPERTIES")

if [[ -z "$preferred_java_binary" ]]; then
    echo "preferred_java_binary is missing from $CONSOLE_PROPERTIES" >&2
    exit 1
fi

if [[ "$preferred_java_binary" == /* ]]; then
    preferred_java_path=$(realpath -m -- "$preferred_java_binary")
else
    preferred_java_path=$(realpath -m -- "$CURRENT_DIR/$preferred_java_binary")
fi

case "$preferred_java_path" in
    "$CONSOLE_HOME"/jre*/bin/java)
        preferred_jre=${preferred_java_path#"$CONSOLE_HOME"/}
        preferred_jre=${preferred_jre%%/*}
        ;;
    *)
        echo "Refusing to prune JREs: preferred_java_binary does not resolve to $CONSOLE_HOME/jre*/bin/java" >&2
        echo "Resolved value: $preferred_java_path" >&2
        exit 1
        ;;
esac

if [[ ! -d "$CONSOLE_HOME/$preferred_jre" ]]; then
    echo "Preferred JRE directory not found: $CONSOLE_HOME/$preferred_jre" >&2
    exit 1
fi

echo "Preparing Forescout Console $version..."
echo "Keeping preferred Java runtime: $preferred_jre"

: > "$ETC_DIR/login.fingerprint.properties"
: > "$ETC_DIR/local.properties"

find "$ETC_DIR" -maxdepth 1 -type f -name 'local.properties*' ! -name 'local.properties' -delete
find "$ETC_DIR" -regextype posix-extended -maxdepth 1 -type d \
    -regex '.*/forescout[0-9]+' -exec rm -rf -- {} +
find "$CONSOLE_HOME" -maxdepth 1 -type d -name 'jre*' \
    ! -name "$preferred_jre" -exec rm -rf -- {} +

find "$CURRENT_DIR" -maxdepth 1 -name 'connect_connect_*' -exec rm -rf -- {} +
find "$CURRENT_DIR" -maxdepth 1 -name 'pluginsetup*' -exec rm -rf -- {} +
find "$GUI_MANAGER_DIR" -maxdepth 1 -name 'new_ver*' -exec rm -rf -- {} +

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
