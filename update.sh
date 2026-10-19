#!/usr/bin/env bash
# Met à jour l'app sur le VPS : récupère le code, reconstruit l'image et vérifie la santé du conteneur.
set -euo pipefail

CONTAINER="lalicornenchantee"
HEALTH_TIMEOUT=90

cd "$(dirname "$(readlink -f "$0")")"

if [ "$(id -u)" -eq 0 ]; then
    echo "Ne lance pas ce script avec sudo : il demandera le mot de passe pour Docker uniquement." >&2
    exit 1
fi

echo "==> Récupération du code"
OLD_REV=$(git rev-parse HEAD)
git pull --ff-only
NEW_REV=$(git rev-parse HEAD)

if [ "$OLD_REV" = "$NEW_REV" ]; then
    echo "Déjà à jour ($(git log -1 --format='%h %s'))."
    if [ "${1:-}" != "--force" ]; then
        echo "Rien à reconstruire. Utilise --force pour reconstruire quand même."
        exit 0
    fi
else
    echo "Nouveaux commits :"
    git log --oneline "$OLD_REV..$NEW_REV"
fi

echo "==> Reconstruction et redémarrage"
sudo docker compose up -d --build

echo "==> Attente de l'état healthy (max ${HEALTH_TIMEOUT}s)"
for _ in $(seq 1 "$HEALTH_TIMEOUT"); do
    STATUS=$(sudo docker inspect "$CONTAINER" --format '{{.State.Health.Status}}' 2>/dev/null || echo "absent")
    if [ "$STATUS" = "healthy" ]; then
        echo "OK : $CONTAINER est healthy."
        sudo docker image prune -f > /dev/null
        exit 0
    fi
    sleep 1
done

echo "ÉCHEC : $CONTAINER est '$STATUS' après ${HEALTH_TIMEOUT}s. Derniers logs :" >&2
sudo docker logs --tail 30 "$CONTAINER" >&2
exit 1
