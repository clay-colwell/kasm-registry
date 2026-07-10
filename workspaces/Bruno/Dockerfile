# syntax=docker/dockerfile:1
ARG BASE_IMAGE
ARG BASE_DIGEST
FROM ${BASE_IMAGE}@${BASE_DIGEST}

ARG BASE_DIGEST

USER root

ENV HOME=/home/kasm-default-profile \
    STARTUPDIR=/dockerstartup \
    DEBIAN_FRONTEND=noninteractive
WORKDIR $HOME

LABEL org.opencontainers.image.title="Bruno for Kasm Workspaces" \
      org.opencontainers.image.base.digest="${BASE_DIGEST}"

RUN mkdir -p /etc/apt/keyrings \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gpg \
    && curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x9FA6017ECABE0266" \
        | gpg --dearmor --yes --output /etc/apt/keyrings/bruno.gpg \
    && chmod 0644 /etc/apt/keyrings/bruno.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/bruno.gpg] http://debian.usebruno.com/ bruno stable" \
        > /etc/apt/sources.list.d/bruno.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends bruno \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0755 "$HOME/Desktop" \
    && find "$HOME/Desktop" -name "*.desktop" -type f -delete \
    && cp /usr/share/applications/bruno.desktop "$HOME/Desktop/bruno.desktop" \
    && sed -i 's#^Exec=.*#Exec=/opt/Bruno/bruno --no-sandbox %U#' "$HOME/Desktop/bruno.desktop" \
    && chmod 0755 "$HOME/Desktop/bruno.desktop" \
    && echo '/usr/bin/desktop_ready && /opt/Bruno/bruno --no-sandbox &' > "$STARTUPDIR/custom_startup.sh" \
    && chmod 0755 "$STARTUPDIR/custom_startup.sh" \
    && chown -R 1000:0 "$HOME" \
    && "$STARTUPDIR/set_user_permission.sh" "$HOME"

ENV HOME=/home/kasm-user
WORKDIR $HOME
RUN mkdir -p "$HOME" && chown -R 1000:0 "$HOME"

USER 1000
CMD ["--tail-log"]
