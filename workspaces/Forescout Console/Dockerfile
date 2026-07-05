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

COPY ["workspaces/Forescout Console/Background.png", "/usr/share/backgrounds/bg_default.png"]
COPY ["workspaces/Forescout Console/xfce4/*", "/home/kasm-default-profile/.config/xfce4/xfconf/xfce-perchannel-xml/"]
COPY ["workspaces/Forescout Console/console/${CONSOLE_ARCHIVE}", "/tmp/forescout-console.tar.gz"]

RUN find $HOME/Desktop -name "*.desktop" -type f -delete \
    && tar -xzf /tmp/forescout-console.tar.gz -C "$HOME" \
    && test -d "$HOME/Forescout Console" \
    && rm /tmp/forescout-console.tar.gz

# Restore the supplied desktop files after removing the core image shortcuts.
COPY ["workspaces/Forescout Console/desktop/*", "/home/kasm-default-profile/Desktop/"]
RUN find "$HOME/Desktop" -name "*.desktop" -type f -exec chmod 0755 {} + \
    && chown -R 1000:1000 "$HOME/Desktop" "$HOME/Forescout Console" \
    && chmod +x "$HOME/Forescout Console/GuiManager/current/Forescout Console" \
    && echo "/usr/bin/desktop_ready && xdg-open \$HOME/Desktop/forescout.desktop" > "$STARTUPDIR/custom_startup.sh" \
    && chmod 0755 "$STARTUPDIR/custom_startup.sh" \
    && chown 1000:0 "$HOME" \
    && "$STARTUPDIR/set_user_permission.sh" "$HOME"

ENV HOME=/home/kasm-user
WORKDIR $HOME
RUN mkdir -p "$HOME" && chown -R 1000:0 "$HOME"

USER 1000
