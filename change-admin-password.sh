#!/usr/bin/env bash

################################################################################
#                                                                              #
#  change-admin-password.sh — смена пароля администратора Contour Glass       #
#                                                                              #
#  Использует werkzeug.security для хеширования пароля.                       #
#                                                                              #
#  Использование:                                                              #
#    sudo ./change-admin-password.sh                                           #
#    sudo ./manage.sh password                                                 #
#                                                                              #
################################################################################

set -euo pipefail

# ============================================================================
# Цвета
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()     { echo -e "${BLUE}[contour-password]${NC} $*"; }
success() { echo -e "${GREEN}[contour-password]${NC} $*"; }
error()   { echo -e "${RED}[contour-password] ОШИБКА:${NC} $*" >&2; }
warn()    { echo -e "${YELLOW}[contour-password]${NC} $*"; }

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

    # Если скрипт запущен из каталога проекта
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

    read -rsp "Введите новый пароль администратора: " NEW_PW
    echo
    if [[ -z "$NEW_PW" ]]; then
        error "Пароль не может быть пустым."
        exit 1
    fi

    read -rsp "Повторите пароль: " NEW_PW2
    echo
    if [[ "$NEW_PW" != "$NEW_PW2" ]]; then
        error "Пароли не совпадают."
        exit 1
    fi

    # Хешируем пароль с помощью werkzeug.security (через Python)
    # Если werkzeug не установлен, используем openssl как fallback
    local hashed_pw
    if python3 -c "import werkzeug.security" 2>/dev/null; then
        hashed_pw=$(python3 -c "
import werkzeug.security
print(werkzeug.security.generate_password_hash('${NEW_PW}'))
")
    else
        warn "werkzeug не найден, устанавливаем..."
        pip3 install werkzeug -q 2>/dev/null || true
        if python3 -c "import werkzeug.security" 2>/dev/null; then
            hashed_pw=$(python3 -c "
import werkzeug.security
print(werkzeug.security.generate_password_hash('${NEW_PW}')
")
        else
            warn "Не удалось установить werkzeug. Пароль будет сохранён в открытом виде."
            hashed_pw="${NEW_PW}"
        fi
    fi

    # Сохраняем хеш пароля в .env
    if grep -q '^CONFIG_ADMIN_PASSWORD=' .env 2>/dev/null; then
        # Экранируем спецсимволы для sed
        local escaped_pw
        escaped_pw=$(echo "$hashed_pw" | sed 's/[\/&]/\\&/g')
        sed -i "s|^CONFIG_ADMIN_PASSWORD=.*$|CONFIG_ADMIN_PASSWORD=${escaped_pw}|" .env
    else
        echo "CONFIG_ADMIN_PASSWORD=${hashed_pw}" >> .env
    fi

    success "Пароль администратора обновлён."

    echo ""
    echo -e "${YELLOW}Перезапустить контейнеры сейчас?${NC}"
    read -r -p "[y/N]: " RESTART
    if [[ "$RESTART" == "yes" ]]; then
        log "Перезапуск контейнеров..."
        docker compose up -d --force-recreate
        success "Контейнеры перезапущены."
    else
        log "Перезапустите приложение позже: docker compose up -d --force-recreate"
    fi
    echo ""
}

main "$@"