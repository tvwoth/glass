#!/usr/bin/env bash

################################################################################
#                                                                              #
#  uninstall.sh — удаление Contour Glass с сервера                            #
#                                                                              #
#  Действия:                                                                   #
#    • запрос подтверждения                                                    #
#    • предложение сохранить пользовательские данные                           #
#    • остановка и удаление Docker-контейнеров, volumes, networks              #
#    • отключение и удаление systemd-юнитов                                    #
#    • удаление директории проекта /opt/glass                                  #
#    • удаление глобальных команд                                              #
#                                                                              #
#  Использование:                                                              #
#    sudo ./uninstall.sh              # Требует подтверждения                  #
#    sudo ./uninstall.sh --force      # Запускает без подтверждения            #
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

log()     { echo -e "${BLUE}[contour-uninstall]${NC} $*"; }
success() { echo -e "${GREEN}[contour-uninstall]${NC} $*"; }
error()   { echo -e "${RED}[contour-uninstall] ОШИБКА:${NC} $*" >&2; }
warn()    { echo -e "${YELLOW}[contour-uninstall]${NC} $*"; }

# ============================================================================
# Функции
# ============================================================================

require_root() {
    if [[ $EUID -ne 0 ]]; then
        if command -v sudo >/dev/null 2>&1; then
            exec sudo bash "$0" "$@"
        fi
        error "Запустите скрипт с правами root (sudo)."
        exit 1
    fi
}

confirm_action() {
    local prompt="$1"
    local force_mode="${2:-false}"

    if [[ "$force_mode" == "true" ]]; then
        return 0
    fi

    local resp
    echo "${prompt}"
    read -r -p "[y/N]: " resp
    if [[ "$resp" != "y" && "$resp" != "yes" ]]; then
        log "Действие отменено."
        exit 0
    fi
}

directory_exists() {
    [[ -d "$1" ]]
}

file_exists() {
    [[ -f "$1" ]]
}

# ============================================================================
# Основная логика
# ============================================================================

main() {
    local force_mode=false

    if [[ "${1:-}" == "--force" ]]; then
        force_mode=true
    fi

    require_root

    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}  Удаление Contour Glass${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""

    APP_DIR="/opt/glass"

    if ! directory_exists "$APP_DIR"; then
        warn "Директория $APP_DIR не найдена."
        log "Приложение уже удалено или не было установлено."
        exit 0
    fi

    success "Найдена директория $APP_DIR"
    echo ""

    # ------------------------------------------------------------------
    # 1. Предложение сохранить пользовательские данные
    # ------------------------------------------------------------------
    local save_data=false
    if [[ "$force_mode" != "true" ]]; then
        local resp
        echo "Сохранить пользовательские конфигурации перед удалением?"
        read -r -p "[y/N]: " resp
        if [[ "$resp" == "yes" ]]; then
            save_data=true
            local backup_dir="${HOME}/contour-backup-$(date +%Y-%m-%d_%H-%M-%S)"
            log "Сохранение пользовательских данных в ${backup_dir}..."

            mkdir -p "$backup_dir"

            if [[ -d "${APP_DIR}/app/user_configs" ]] && [[ -n "$(ls -A "${APP_DIR}/app/user_configs" 2>/dev/null)" ]]; then
                cp -r "${APP_DIR}/app/user_configs" "${backup_dir}/configs" 2>/dev/null || true
                log "  configs/ сохранены"
            fi

            if [[ -d "${APP_DIR}/storage" ]] && [[ -n "$(ls -A "${APP_DIR}/storage" 2>/dev/null)" ]]; then
                cp -r "${APP_DIR}/storage" "${backup_dir}/storage" 2>/dev/null || true
                log "  storage/ сохранён"
            fi

            if [[ -d "${APP_DIR}/exports" ]] && [[ -n "$(ls -A "${APP_DIR}/exports" 2>/dev/null)" ]]; then
                cp -r "${APP_DIR}/exports" "${backup_dir}/exports" 2>/dev/null || true
                log "  exports/ сохранены"
            fi

            if [[ -f "${APP_DIR}/.env" ]]; then
                cp "${APP_DIR}/.env" "${backup_dir}/.env" 2>/dev/null || true
                log "  .env сохранён"
            fi

            success "Пользовательские данные сохранены в: ${backup_dir}"
        fi
    fi

    # ------------------------------------------------------------------
    # 2. Подтверждение удаления
    # ------------------------------------------------------------------
    confirm_action "Удалить полностью приложение Contour Glass?" "$force_mode"
    echo ""

    # ------------------------------------------------------------------
    # 3. Остановка Docker-контейнеров
    # ------------------------------------------------------------------
    log "Останавливаем Docker-контейнеры..."
    if directory_exists "$APP_DIR" && file_exists "${APP_DIR}/docker-compose.yml"; then
        cd "$APP_DIR"
        if docker compose down -v --remove-orphans 2>/dev/null || docker-compose down -v --remove-orphans 2>/dev/null || true; then
            success "Docker-контейнеры остановлены и удалены."
        else
            warn "Не удалось остановить контейнеры."
        fi
    else
        warn "docker-compose.yml не найден, пропускаем."
    fi

    # ------------------------------------------------------------------
    # 4. Удаление Nginx-конфигов
    # ------------------------------------------------------------------
    log "Удаляем конфиги Nginx..."
    rm -f /etc/nginx/sites-enabled/contour* /etc/nginx/sites-available/contour* \
          /etc/nginx/sites-enabled/glass* /etc/nginx/sites-available/glass* 2>/dev/null || true
    systemctl reload nginx 2>/dev/null || true
    success "Конфиги Nginx удалены."

    # ------------------------------------------------------------------
    # 5. Отключение и удаление systemd-юнитов
    # ------------------------------------------------------------------
    log "Отключаем и удаляем systemd-юниты..."

    local units_to_remove=(
        "contour-update.timer"
        "contour-update.service"
        "contour.service"
        "glass-update.timer"
        "glass-update.service"
        "glass.service"
    )

    for unit in "${units_to_remove[@]}"; do
        if systemctl is-enabled "$unit" &>/dev/null 2>&1 || systemctl is-active "$unit" &>/dev/null 2>&1; then
            log "  • $unit..."
            systemctl stop "$unit" 2>/dev/null || true
            systemctl disable "$unit" 2>/dev/null || true
            rm -f "/etc/systemd/system/$unit" 2>/dev/null || true
            success "    $unit удалена"
        fi
    done

    systemctl daemon-reload 2>/dev/null || true
    systemctl reset-failed 2>/dev/null || true

    # ------------------------------------------------------------------
    # 6. Удаление директории проекта
    # ------------------------------------------------------------------
    log "Удаляем директорию проекта..."
    if directory_exists "$APP_DIR"; then
        rm -rf "$APP_DIR"
        success "$APP_DIR полностью удалена"
    else
        warn "Директория $APP_DIR уже не существует"
    fi

    # ------------------------------------------------------------------
    # 7. Удаление глобальных команд
    # ------------------------------------------------------------------
    log "Удаляем команды из /usr/local/bin..."
    rm -f /usr/local/bin/contour-install /usr/local/bin/contour-update \
          /usr/local/bin/contour-uninstall /usr/local/bin/contour-change-password \
          /usr/local/bin/contour-reset-password \
          /usr/local/bin/glass-install /usr/local/bin/glass-update \
          /usr/local/bin/glass-uninstall /usr/local/bin/glass-change-password 2>/dev/null || true
    success "Глобальные команды удалены."

    # ------------------------------------------------------------------
    # 8. Очистка Docker (опционально)
    # ------------------------------------------------------------------
    if confirm_action "Очистить неиспользуемые объекты Docker (prune)?" "$force_mode"; then
        log "Выполняем docker system prune --volumes..."
        docker system prune -f --volumes 2>/dev/null || true
        success "Docker очищен."
    fi

    echo ""
    success "============================================"
    success "  Приложение Contour Glass успешно удалено!"
    success "============================================"
    echo ""

    if [[ "$save_data" == "true" ]]; then
        log "Пользовательские данные сохранены. Для восстановления скопируйте их обратно."
    fi
    echo ""
}

main "$@"