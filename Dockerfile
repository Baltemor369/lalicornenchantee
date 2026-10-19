FROM caddy:2.11-alpine

# Caddy n'a pas besoin d'écrire ailleurs que dans /tmp pour servir des fichiers statiques
ENV XDG_CONFIG_HOME=/tmp/config \
    XDG_DATA_HOME=/tmp/data

COPY Caddyfile /etc/caddy/Caddyfile
COPY public/ /srv/

USER nobody

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1:8501/ || exit 1
