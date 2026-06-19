#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
if [[ ! -t 1 ]]; then RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''; fi

log()       { echo -e "${BLUE}[contour-password]${NC} $*"; }
success()   { echo -e "${GREEN}[contour-password]${NC} $*"; }
error()     { echo -e "${RED}[contour-password] ОШИБКА:${NC} $*" >&2; }
warn()      { echo -e "${YELLOW}[contour-password]${NC} $*"; }

require_root() {
    if [[ $EUID -ne 0 ]]; then
        if command -v sudo >/dev/null 2>&1; then
            exec sudo bash "$0" "$@"
        fi
        error "Запустите скрипт с правами root (sudo)."
        exit 1
    fi
}

main() {
    require_root "$@"

    APP_DIR="/opt/glass"
    if [[ -f .env ]]; then
        APP_DIR="$(pwd)"
    elif [[ -d "$APP_DIR" ]]; then
        cd "$APP_DIR"
    else
        error "Не найден каталог установки (/opt/glass)."
        error "Запустите скрипт из каталога проекта или из /opt/glass."
        exit 1
    fi

    if [[ ! -f .env ]]; then
        error "Файл .env не найден в $APP_DIR"
        exit 1
    fi

    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Смена пароля администратора${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""

    if ! python3 -c "import werkzeug" 2>/dev/null; then
        error "werkzeug не установлен. Хеширование пароля невозможно."
        error "Установите: pip install werkzeug"
        error "Или: apt-get install python3-werkzeug (Ubuntu/Debian)"
        exit 1
    fi

    while true; do
        read -rsp "Введите новый пароль администратора (минимум 4 символа): " NEW_PW
        echo
        if [[ ${#NEW_PW} -lt 4 ]]; then
            warn "Ошибка: пароль должен содержать минимум 4 символа."
            continue
        fi
        read -rsp "Повторите пароль: " NEW_PW2
        echo
        if [[ "$NEW_PW" != "$NEW_PW2" ]]; then
            warn "Ошибка: пароли не совпадают."
            continue
        fi
        break
    done

    if grep -q '^CONFIG_ADMIN_PASSWORD=' .env 2>/dev/null; then
        sed -i "s|^CONFIG_ADMIN_PASSWORD=.*$|CONFIG_ADMIN_PASSWORD=${NEW_PW}|" .env
    else
        echo "CONFIG_ADMIN_PASSWORD=${NEW_PW}" >> .env
    fi

    success "Пароль администратора обновлён."

    echo ""
    echo "Перезапустить контейнеры сейчас?"
    read -r -p "[y/N]: " RESTART
    if [[ "$RESTART" == "y" || "$RESTART" == "yes" ]]; then
        log "Перезапуск контейнеров..."
        docker compose up -d --force-recreate
        success "Контейнеры перезапущены."
    else
        log "Перезапустите приложение позже: docker compose up -d --force-recreate"
    fi
    echo ""
}

main "$@"