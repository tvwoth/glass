#!/usr/bin/env bash

################################################################################
#                                                                              #
#  reset-admin-password.sh — сброс пароля администратора Contour Glass        #
#                                                                              #
#  Сбрасывает пароль администратора до значения по умолчанию: admin           #
#                                                                              #
#  ВАЖНО: Сброс возможен только локально на сервере.                          #
#                                                                              #
#  После сброса:                                                              #
#    • пароль = admin                                                          #
#    • для вступления в силу требуется перезапуск контейнера                   #
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

log()     { echo -e "${BLUE}[contour-reset]${NC} $*"; }
success() { echo -e "${GREEN}[contour-reset]${NC} $*"; }
error()   { echo -e "${RED}[contour-reset] ОШИБКА:${NC} $*" >&2; }
warn()    { echo -e "${YELLOW}[contour-reset]${NC} $*"; }

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

    echo ""
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}  Сброс пароля администратора${NC}"
    echo -e "${YELLOW}============================================${NC}"
    echo ""
    echo -e "${RED}ВНИМАНИЕ:${NC} Пароль будет сброшен до значения ${YELLOW}admin${NC}"
    echo ""

    local resp
    read -r -p "Вы уверены? (yes/no): " resp
    if [[ "$resp" != "yes" ]]; then
        log "Сброс отменён."
        exit 0
    fi

    if grep -q '^CONFIG_ADMIN_PASSWORD=' .env 2>/dev/null; then
        # Удаляем строку с паролем
        sed -i '/^CONFIG_ADMIN_PASSWORD=/d' .env
    fi

    # Добавляем пароль по умолчанию
    echo "CONFIG_ADMIN_PASSWORD=admin" >> .env
    success "Пароль сброшен до значения: admin"

    echo ""
    read -r -p "${YELLOW}Перезапустить контейнеры сейчас? (yes/no): ${NC}" RESTART
    if [[ "$RESTART" == "yes" ]]; then
        log "Перезапуск контейнеров..."
        docker compose up -d --force-recreate
        success "Контейнеры перезапущены."
    else
        log "Перезапустите приложение позже: docker compose up -d --force-recreate"
    fi

    echo ""
    log "Пароль администратора: admin"
    echo ""
}

main "$@"