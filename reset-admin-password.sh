#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
if [[ ! -t 1 ]]; then RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''; fi

log_error() { echo -e "${RED}[glass-reset] ОШИБКА:${NC} $*" >&2; }
log_warn()  { echo -e "${YELLOW}[glass-reset]${NC} $*"; }

APP_DIR="${GLASS_APP_DIR:-/opt/glass}"
if [[ ! -d "$APP_DIR" ]]; then APP_DIR="$(cd "$(dirname "$0")" && pwd)"; fi
cd "$APP_DIR"

if [[ ! -f .env ]]; then log_error "Файл .env не найден в $APP_DIR"; exit 1; fi

echo ""
echo -e "${RED}============================================${NC}"
echo -e "${RED}  СБРОС ПАРОЛЯ АДМИНИСТРАТОРА${NC}"
echo -e "${RED}============================================${NC}"
echo ""

if ! python3 -c "import werkzeug" 2>/dev/null; then
    echo "werkzeug не установлен. Устанавливаем..."
    pip3 install werkzeug 2>/dev/null || pip install werkzeug 2>/dev/null || \
        apt-get install -y python3-werkzeug 2>/dev/null || {
        echo "Не удалось установить werkzeug. Хеширование пароля невозможно."
        exit 1
    }
    echo "werkzeug установлен."
fi

log_warn "Вы уверены, что хотите сбросить пароль администратора?"
if [[ "${1:-}" != "--force" ]] && [[ "${1:-}" != "-f" ]]; then
    read -r -p "Продолжить? [y/N]: " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "yes" ]]; then
        echo "Операция отменена."
        exit 0
    fi
fi

NEW_PW=$(openssl rand -base64 12 2>/dev/null | tr -dc 'a-zA-Z0-9' || echo "ContourReset123!")
if [[ ${#NEW_PW} -lt 4 ]]; then NEW_PW="ContourReset123!"; fi

HASHED_PW=$(python3 -c "import werkzeug.security; print(werkzeug.security.generate_password_hash('${NEW_PW}'))")
if grep -q '^CONFIG_ADMIN_PASSWORD=' .env 2>/dev/null; then
    sed -i "s|^CONFIG_ADMIN_PASSWORD=.*$|CONFIG_ADMIN_PASSWORD=${HASHED_PW}|" .env
else
    echo "CONFIG_ADMIN_PASSWORD=${HASHED_PW}" >> .env
fi

echo -e "${GREEN}Пароль сброшен: ${NEW_PW}${NC}"
echo -e "${YELLOW}Сохраните этот пароль!${NC}"

read -r -p "Перезапустить контейнеры сейчас? [y/N]: " RESTART
if [[ "$RESTART" == "y" || "$RESTART" == "yes" ]]; then
    docker compose up -d --force-recreate
    echo -e "${GREEN}Контейнеры перезапущены.${NC}"
else
    echo "Перезапустите позже: docker compose up -d --force-recreate"
fi