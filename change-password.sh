#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
if [[ ! -t 1 ]]; then RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''; fi

log_error() { echo -e "${RED}[glass-password] ОШИБКА:${NC} $*" >&2; }

APP_DIR="${GLASS_APP_DIR:-/opt/glass}"
if [[ ! -d "$APP_DIR" ]]; then APP_DIR="$(cd "$(dirname "$0")" && pwd)"; fi
cd "$APP_DIR"

if [[ ! -f .env ]]; then log_error "Файл .env не найден в $APP_DIR"; exit 1; fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Смена пароля администратора${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

if ! python3 -c "import werkzeug" 2>/dev/null; then
    log_error "werkzeug не установлен. Хеширование пароля невозможно."
    log_error "Установите: pip install werkzeug"
    log_error "Или: apt-get install python3-werkzeug (Ubuntu/Debian)"
    exit 1
fi

while true; do
    read -rsp "Введите новый пароль администратора (минимум 4 символа): " NEW_PW
    echo
    if [[ ${#NEW_PW} -lt 4 ]]; then
        echo -e "${YELLOW}Ошибка: пароль должен содержать минимум 4 символа.${NC}"
        continue
    fi
    read -rsp "Повторите пароль: " NEW_PW2
    echo
    if [[ "$NEW_PW" != "$NEW_PW2" ]]; then
        echo -e "${YELLOW}Ошибка: пароли не совпадают.${NC}"
        continue
    fi
    break
done

if grep -q '^CONFIG_ADMIN_PASSWORD=' .env 2>/dev/null; then
    sed -i "s|^CONFIG_ADMIN_PASSWORD=.*$|CONFIG_ADMIN_PASSWORD=${NEW_PW}|" .env
else
    echo "CONFIG_ADMIN_PASSWORD=${NEW_PW}" >> .env
fi

echo -e "${GREEN}Пароль администратора обновлён в .env${NC}"

read -r -p "Перезапустить контейнеры сейчас? [y/N]: " RESTART
if [[ "$RESTART" == "y" || "$RESTART" == "yes" ]]; then
    docker compose up -d --force-recreate
    echo -e "${GREEN}Контейнеры перезапущены.${NC}"
else
    echo "Перезапустите позже: docker compose up -d --force-recreate"
fi