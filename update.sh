#!/usr/bin/env bash

################################################################################
#                                                                              #
#  update.sh — безопасное обновление Contour Glass                            #
#                                                                              #
#  Действия:                                                                   #
#    • проверка root                                                           #
#    • создание резервной копии configs/, storage/, exports/, .env             #
#    • скачивание свежего кода из Git                                           #
#    • восстановление прав на скрипты                                           #
#    • пересборка и перезапуск стека                                           #
#                                                                              #
#  При ошибке:                                                                 #
#    • остановка обновления                                                    #
#    • сохранение резервной копии                                               #
#    • вывод причины ошибки                                                    #
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

log()     { echo -e "${BLUE}[contour-update]${NC} $*"; }
success() { echo -e "${GREEN}[contour-update]${NC} $*"; }
error()   { echo -e "${RED}[contour-update] ОШИБКА:${NC} $*" >&2; }
warn()    { echo -e "${YELLOW}[contour-update]${NC} $*"; }

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

create_backup() {
    local app_dir="$1"
    local backup_dir="${app_dir}/backup/$(date +%Y-%m-%d_%H-%M-%S)"

    log "Создание резервной копии в ${backup_dir}..."

    mkdir -p "$backup_dir"

    # Резервное копирование пользовательских данных
    if [[ -d "${app_dir}/app/user_configs" ]] && [[ -n "$(ls -A "${app_dir}/app/user_configs" 2>/dev/null)" ]]; then
        cp -r "${app_dir}/app/user_configs" "${backup_dir}/configs" 2>/dev/null || true
        log "  configs/ сохранены"
    fi

    if [[ -d "${app_dir}/storage" ]] && [[ -n "$(ls -A "${app_dir}/storage" 2>/dev/null)" ]]; then
        cp -r "${app_dir}/storage" "${backup_dir}/storage" 2>/dev/null || true
        log "  storage/ сохранён"
    fi

    if [[ -d "${app_dir}/exports" ]] && [[ -n "$(ls -A "${app_dir}/exports" 2>/dev/null)" ]]; then
        cp -r "${app_dir}/exports" "${backup_dir}/exports" 2>/dev/null || true
        log "  exports/ сохранены"
    fi

    if [[ -f "${app_dir}/.env" ]]; then
        cp "${app_dir}/.env" "${backup_dir}/.env" 2>/dev/null || true
        log "  .env сохранён"
    fi

    success "Резервная копия создана: ${backup_dir}"
    echo "${backup_dir}"
}

# ============================================================================
# Основная логика
# ============================================================================

main() {
    require_root "$@"

    APP_DIR="/opt/glass"

    if [[ ! -d "$APP_DIR" ]]; then
        error "Каталог $APP_DIR не найден. Установите приложение через install.sh."
        exit 1
    fi

    cd "$APP_DIR"

    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Обновление Contour Glass${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""

    # ------------------------------------------------------------------
    # 1. Создание резервной копии
    # ------------------------------------------------------------------
    local backup_path
    backup_path=$(create_backup "$APP_DIR")
    log "Резервная копия: ${backup_path}"

    # ------------------------------------------------------------------
    # 2. Получение последних изменений из Git
    # ------------------------------------------------------------------
    log "Получаем последние изменения из Git..."
    if ! git pull --ff-only origin "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'main')"; then
        error "Не удалось обновить код из Git. Резервная копия сохранена: ${backup_path}"
        exit 1
    fi
    success "Код обновлён."

    # ------------------------------------------------------------------
    # 3. Восстановление прав на скрипты
    # ------------------------------------------------------------------
    log "Восстанавливаем права на скрипты..."
    chmod +x "$APP_DIR"/*.sh || true

    # ------------------------------------------------------------------
    # 4. Обновление глобальных команд
    # ------------------------------------------------------------------
    mkdir -p /usr/local/bin
    ln -sf "$APP_DIR/install.sh"                /usr/local/bin/contour-install
    ln -sf "$APP_DIR/update.sh"                 /usr/local/bin/contour-update
    ln -sf "$APP_DIR/uninstall.sh"              /usr/local/bin/contour-uninstall
    ln -sf "$APP_DIR/change-admin-password.sh"  /usr/local/bin/contour-change-password
    ln -sf "$APP_DIR/reset-admin-password.sh"   /usr/local/bin/contour-reset-password

    # ------------------------------------------------------------------
    # 5. Проверка .env
    # ------------------------------------------------------------------
    if [[ -f .env ]]; then
        if ! grep -q '^CONFIG_ADMIN_PASSWORD=' .env 2>/dev/null; then
            read -rsp "Пароль администратора отсутствует. Введите пароль (Enter = admin): " ADMIN_PW
            echo
            ADMIN_PW=${ADMIN_PW:-admin}
            echo "CONFIG_ADMIN_PASSWORD=${ADMIN_PW}" >> .env
            success "Пароль администратора добавлен в .env"
        fi
        if ! grep -q '^SECRET_KEY=' .env 2>/dev/null; then
            SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
            echo "SECRET_KEY=${SECRET_KEY}" >> .env
            log "SECRET_KEY сгенерирован."
        fi
    fi

    # ------------------------------------------------------------------
    # 6. Создание каталогов и прав
    # ------------------------------------------------------------------
    mkdir -p "$APP_DIR/data/user_configs"
    chown -R 1000:1000 "$APP_DIR/data/user_configs" 2>/dev/null || true
    chmod 755 "$APP_DIR/data/user_configs" 2>/dev/null || true

    # ------------------------------------------------------------------
    # 7. Сборка и перезапуск
    # ------------------------------------------------------------------
    log "Останавливаем старые контейнеры..."
    docker compose down --remove-orphans 2>/dev/null || true

    log "Сборка образов и перезапуск стека..."
    if ! docker compose up -d --build --force-recreate; then
        error "Не удалось перезапустить контейнеры. Резервная копия сохранена: ${backup_path}"
        docker compose logs --tail 20 glass 2>/dev/null || true
        exit 1
    fi

    # ------------------------------------------------------------------
    # 8. Ожидание запуска
    # ------------------------------------------------------------------
    log "Ожидание запуска контейнера..."
    local wait_count=0
    while true; do
        STATUS=$(docker inspect --format='{{.State.Status}}' glass 2>/dev/null || echo "")
        if [[ "$STATUS" == "running" ]]; then
            break
        fi
        sleep 3
        wait_count=$((wait_count + 1))
        if [[ $wait_count -ge 20 ]]; then
            error "Контейнер не запустился. Резервная копия сохранена: ${backup_path}"
            docker logs --tail 30 glass 2>/dev/null || true
            exit 1
        fi
    done

    # Проверка healthcheck
    local health_wait=0
    while true; do
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' glass 2>/dev/null || echo "")
        if [[ -z "$HEALTH" ]] || [[ "$HEALTH" == "healthy" ]]; then
            break
        fi
        sleep 3
        health_wait=$((health_wait + 1))
        if [[ $health_wait -ge 15 ]]; then
            warn "Контейнер запущен, но healthcheck не пройден."
            docker logs --tail 20 glass 2>/dev/null || true
            break
        fi
    done

    # ------------------------------------------------------------------
    # 9. Статус
    # ------------------------------------------------------------------
    echo ""
    log "Текущий статус:"
    docker compose ps 2>/dev/null || true

    echo ""
    success "============================================"
    success "  Обновление завершено"
    success "============================================"
    echo ""
    log "Резервная копия: ${backup_path}"
    log "Резервные копии не удаляются автоматически."
    echo ""
}

main "$@"