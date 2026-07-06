# syntax=docker/dockerfile:1
ARG BASE_IMAGE
ARG BASE_DIGEST
FROM ${BASE_IMAGE}@${BASE_DIGEST}

ARG CONSOLE_ARCHIVE
ARG BASE_DIGEST

USER root

ENV HOME=/home/kasm-default-profile
ENV STARTUPDIR=/dockerstartup
WORKDIR $HOME

LABEL org.opencontainers.image.title="Forescout Console for Kasm Workspaces" \
      org.opencontainers.image.base.digest="${BASE_DIGEST}"

RUN dnf upgrade -y \
    && wget -q https://raw.githubusercontent.com/kasmtech/workspaces-images/develop/src/ubuntu/install/chromium/install_chromium.sh -O /tmp/install_chromium.sh \
    && DISTRO=fedora43 SKIP_CLEAN=1 bash /tmp/install_chromium.sh \
    && rm -f /tmp/install_chromium.sh \
    && wget -q https://raw.githubusercontent.com/kasmtech/workspaces-images/develop/src/oracle/install/vs_code/install_vs_code.sh -O /tmp/install_vs_code.sh \
    && DISTRO=fedora43 SKIP_CLEAN=1 bash /tmp/install_vs_code.sh \
    && rm -f /tmp/install_vs_code.sh \
    && dnf clean all \
    && mkdir -p ~/.config/xfce4 \
    && echo "WebBrowser=chromium" > ~/.config/xfce4/helpers.rc

COPY ["workspaces/Forescout Console/Background.png", "/usr/share/backgrounds/bg_default.png"]
COPY ["workspaces/Forescout Console/xfce4/*", "/home/kasm-default-profile/.config/xfce4/xfconf/xfce-perchannel-xml/"]
ADD --chown=1000:1000 ["workspaces/Forescout Console/console/${CONSOLE_ARCHIVE}", "/home/kasm-default-profile/"]
COPY ["workspaces/Forescout Console/package_updated_console.sh", "/usr/local/bin/package-forescout-console"]

RUN find $HOME/Desktop -name "*.desktop" -type f -delete \
    && test -d "$HOME/Forescout Console" \
    && wget -q https://raw.githubusercontent.com/kasmtech/workspaces-images/develop/src/ubuntu/install/cleanup/cleanup.sh -O /tmp/cleanup.sh \
    && DISTRO=fedora43 bash /tmp/cleanup.sh

# Restore the supplied desktop files after removing the core image shortcuts.
COPY ["workspaces/Forescout Console/desktop/*", "/home/kasm-default-profile/Desktop/"]
RUN find "$HOME/Desktop" -name "*.desktop" -type f -exec chmod 0755 {} + \
    && chown -R 1000:1000 "$HOME/Desktop" "$HOME/Forescout Console" \
    && chmod +x "$HOME/Forescout Console/GuiManager/current/Forescout Console" \
    && chmod 0755 /usr/local/bin/package-forescout-console \
    && echo "/usr/bin/desktop_ready && eval \$(grep '^Exec=' \"\$HOME/Desktop/forescout.desktop\" | tail -1 | sed 's/^Exec=//' | sed 's/%[fFuU]//g') &" > "$STARTUPDIR/custom_startup.sh" \
    && chmod 0755 "$STARTUPDIR/custom_startup.sh" \
    && chown 1000:0 "$HOME" \
    && "$STARTUPDIR/set_user_permission.sh" "$HOME"

ENV HOME=/home/kasm-user
WORKDIR $HOME
RUN mkdir -p "$HOME" && chown -R 1000:0 "$HOME"

USER 1000
