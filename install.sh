#!/usr/bin/env bash

################################################################################
#                                                                              #
#  install.sh — автоматическая установка Contour Glass                        #
#                                                                              #
#  Поддерживаемые системы:                                                     #
#    • Ubuntu 22.04 LTS, 24.04 LTS, 26.04 LTS                                 #
#    • Debian 12, 13                                                           #
#    • Linux Mint (на базе Ubuntu LTS)                                         #
#    • Arch Linux (rolling release)                                            #
#    • AlmaLinux 9+, Rocky Linux 9+, Fedora 40+                                #
#                                                                              #
#  Выполняет:                                                                  #
#    • определение дистрибутива и пакетного менеджера                          #
#    • проверку доступности сети, git, curl, docker, python3                   #
#    • установку недостающих компонентов через официальные репозитории         #
#    • проверку свободного порта                                               #
#    • клонирование/обновление репозитория в /opt/glass                        #
#    • создание .env с паролем администратора                                  #
#    • запуск Docker-стека                                                     #
#                                                                              #
#  Скрипт идемпотентен: повторный запуск не удаляет данные и конфигурации.    #
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

log()     { echo -e "${BLUE}[contour-install]${NC} $*"; }
success() { echo -e "${GREEN}[contour-install]${NC} $*"; }
error()   { echo -e "${RED}[contour-install] ОШИБКА:${NC} $*" >&2; }
warn()    { echo -e "${YELLOW}[contour-install]${NC} $*"; }

# ============================================================================
# Вспомогательные функции
# ============================================================================

require_root() {
    if [[ $EUID -ne 0 ]]; then
        if command -v sudo >/dev/null 2>&1; then
            log "Перезапускаем скрипт через sudo..."
            exec sudo bash "$0" "$@"
        fi
        error "Запустите скрипт с правами root (sudo)."
        exit 1
    fi
}

check_cmd() {
    command -v "$1" >/dev/null 2>&1
}

confirm() {
    local msg="$1"
    local resp
    read -r -p "${YELLOW}${msg} (yes/no): ${NC}" resp
    [[ "$resp" == "yes" ]]
}

is_port_busy() {
    local port="$1"
    if command -v ss >/dev/null 2>&1; then
        ss -ltn 2>/dev/null | awk '{print $4}' | awk -F: '{print $NF}' | grep -qE "^${port}$"
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tln 2>/dev/null | awk '{print $4}' | awk -F: '{print $NF}' | grep -qE "^${port}$"
    else
        # fallback: try connecting
        timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/${port}" 2>/dev/null && return 0 || return 1
    fi
}

# ============================================================================
# Определение дистрибутива
# ============================================================================

detect_distro() {
    local id="" id_like="" version=""

    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        id="${ID,,}"
        id_like="${ID_LIKE,,}"
        version="${VERSION_ID}"
    elif [[ -f /etc/lsb-release ]]; then
        . /etc/lsb-release
        id="${DISTRIB_ID,,}"
        version="${DISTRIB_RELEASE}"
    fi

    # Ubuntu
    if [[ "$id" == "ubuntu" || "$id_like" == *"ubuntu"* ]]; then
        if [[ "$id" == "linuxmint" || "$id" == "mint" ]]; then
            echo "linuxmint"
            return
        fi
        echo "ubuntu"
        return
    fi

    # Debian
    if [[ "$id" == "debian" || "$id_like" == *"debian"* ]]; then
        echo "debian"
        return
    fi

    # Arch
    if [[ "$id" == "arch" || "$id_like" == *"arch"* ]]; then
        echo "arch"
        return
    fi

    # Fedora
    if [[ "$id" == "fedora" ]]; then
        echo "fedora"
        return
    fi

    # AlmaLinux / Rocky
    if [[ "$id" == "almalinux" || "$id" == "rocky" || "$id_like" == *"rhel"* || "$id_like" == *"fedora"* ]]; then
        if [[ "$id" == "almalinux" ]]; then
            echo "almalinux"
            return
        fi
        if [[ "$id" == "rocky" ]]; then
            echo "rocky"
            return
        fi
        echo "rhel"
        return
    fi

    echo "unknown"
}

detect_pkg_manager() {
    local distro="$1"
    case "$distro" in
        ubuntu|debian|linuxmint) echo "apt" ;;
        arch)                    echo "pacman" ;;
        fedora|almalinux|rocky|rhel) echo "dnf" ;;
        *)                       echo "unknown" ;;
    esac
}

# ============================================================================
# Проверка сети
# ============================================================================

check_network() {
    log "Проверка доступности сети..."
    if command -v curl >/dev/null 2>&1; then
        if curl -s --connect-timeout 5 https://google.com >/dev/null 2>&1; then
            success "Сеть доступна."
            return 0
        fi
    fi
    if command -v wget >/dev/null 2>&1; then
        if wget -q --timeout=5 https://google.com -O /dev/null 2>&1; then
            success "Сеть доступна."
            return 0
        fi
    fi
    # ping fallback
    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        success "Сеть доступна."
        return 0
    fi
    error "Сеть недоступна. Проверьте подключение к интернету."
    exit 1
}

# ============================================================================
# Установка пакетов в зависимости от дистрибутива
# ============================================================================

install_packages_distro() {
    local distro="$1"
    local pkg_manager="$2"
    local packages=("$@")
    # remove first two args (distro, pkg_manager)
    packages=("${packages[@]:2}")

    log "Установка пакетов: ${packages[*]}"

    case "$pkg_manager" in
        apt)
            DEBIAN_FRONTEND=noninteractive apt-get update -y
            DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"
            ;;
        pacman)
            pacman -Sy --noconfirm "${packages[@]}"
            ;;
        dnf)
            dnf install -y "${packages[@]}"
            ;;
        *)
            error "Неизвестный пакетный менеджер: $pkg_manager"
            exit 1
            ;;
    esac
}

# ============================================================================
# Установка Docker
# ============================================================================

install_docker() {
    local distro="$1"
    local pkg_manager="$2"

    if check_cmd docker; then
        log "Docker уже установлен."
        return 0
    fi

    log "Установка Docker..."

    case "$distro" in
        ubuntu|debian|linuxmint)
            # Установка через официальный репозиторий Docker
            if ! grep -Rq "download.docker.com" /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null; then
                log "Добавляем официальный репозиторий Docker..."
                mkdir -p /etc/apt/keyrings
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
                    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
                    | tee /etc/apt/sources.list.d/docker.list > /dev/null
                apt-get update -y
            fi
            DEBIAN_FRONTEND=noninteractive apt-get install -y \
                docker-ce docker-ce-cli containerd.io \
                docker-buildx-plugin docker-compose-plugin
            ;;
        arch)
            pacman -Sy --noconfirm docker docker-compose
            ;;
        fedora|almalinux|rocky|rhel)
            dnf install -y dnf-plugins-core
            if ! grep -Rq "download.docker.com" /etc/yum.repos.d 2>/dev/null; then
                dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            fi
            dnf install -y docker-ce docker-ce-cli containerd.io \
                docker-buildx-plugin docker-compose-plugin
            ;;
    esac

    # Запуск Docker
    systemctl enable docker --now 2>/dev/null || true

    # Ожидание запуска Docker
    local wait_count=0
    while ! docker version >/dev/null 2>&1; do
        sleep 2
        wait_count=$((wait_count + 1))
        if [[ $wait_count -ge 15 ]]; then
            error "Docker не запустился после установки."
            exit 1
        fi
    done

    success "Docker успешно установлен и запущен."
}

# ============================================================================
# Проверка и установка компонентов
# ============================================================================

ensure_component() {
    local cmd="$1"
    local name="$2"
    local distro="$3"
    local pkg_manager="$4"
    shift 4
    local pkg_names=("$@")

    if check_cmd "$cmd"; then
        log "${name} уже установлен."
        return 0
    fi

    warn "${name} не найден."
    if confirm "Установить ${name}?"; then
        install_packages_distro "$distro" "$pkg_manager" "${pkg_names[@]}"
        if check_cmd "$cmd"; then
            success "${name} установлен."
            return 0
        else
            error "Не удалось установить ${name}."
            exit 1
        fi
    else
        error "Без ${name} установка невозможна."
        exit 1
    fi
}

# ============================================================================
# Проверка порта
# ============================================================================

check_port() {
    local port="$1"
    if is_port_busy "$port"; then
        warn "Порт $port уже занят."
        return 1
    fi
    return 0
}

prompt_port() {
    local default_port="$1"
    local port
    while true; do
        read -rp "Введите порт приложения [${default_port}]: " port
        port=${port:-$default_port}
        if [[ ! "$port" =~ ^[0-9]+$ ]] || [[ "$port" -lt 1 ]] || [[ "$port" -gt 65535 ]]; then
            warn "Порт должен быть числом от 1 до 65535."
            continue
        fi
        if is_port_busy "$port"; then
            warn "Порт $port занят. Выберите другой порт."
            continue
        fi
        echo "$port"
        return
    done
}

# ============================================================================
# Основная логика
# ============================================================================

main() {
    require_root "$@"

    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Установка Contour Glass${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""

    # ------------------------------------------------------------------
    # 1. Определение дистрибутива
    # ------------------------------------------------------------------
    DISTRO=$(detect_distro)
    PKG_MANAGER=$(detect_pkg_manager "$DISTRO")

    log "Определён дистрибутив: ${DISTRO}"
    log "Пакетный менеджер: ${PKG_MANAGER}"

    if [[ "$DISTRO" == "unknown" ]]; then
        error "Не удалось определить дистрибутив Linux."
        error "Поддерживаются: Ubuntu, Debian, Linux Mint, Arch Linux, Fedora, AlmaLinux, Rocky Linux."
        exit 1
    fi

    if [[ "$PKG_MANAGER" == "unknown" ]]; then
        error "Не удалось определить пакетный менеджер."
        exit 1
    fi

    # ------------------------------------------------------------------
    # 2. Проверка сети
    # ------------------------------------------------------------------
    check_network

    # ------------------------------------------------------------------
    # 3. Проверка/установка компонентов
    # ------------------------------------------------------------------
    case "$PKG_MANAGER" in
        apt)
            ensure_component "git"    "Git"    "$DISTRO" "$PKG_MANAGER" "git"
            ensure_component "curl"   "curl"   "$DISTRO" "$PKG_MANAGER" "curl"
            ensure_component "python3" "Python 3" "$DISTRO" "$PKG_MANAGER" "python3"
            # openssl для генерации SECRET_KEY
            ensure_component "openssl" "OpenSSL" "$DISTRO" "$PKG_MANAGER" "openssl"
            ;;
        pacman)
            ensure_component "git"    "Git"    "$DISTRO" "$PKG_MANAGER" "git"
            ensure_component "curl"   "curl"   "$DISTRO" "$PKG_MANAGER" "curl"
            ensure_component "python3" "Python 3" "$DISTRO" "$PKG_MANAGER" "python"
            ensure_component "openssl" "OpenSSL" "$DISTRO" "$PKG_MANAGER" "openssl"
            ;;
        dnf)
            ensure_component "git"    "Git"    "$DISTRO" "$PKG_MANAGER" "git"
            ensure_component "curl"   "curl"   "$DISTRO" "$PKG_MANAGER" "curl"
            ensure_component "python3" "Python 3" "$DISTRO" "$PKG_MANAGER" "python3"
            ensure_component "openssl" "OpenSSL" "$DISTRO" "$PKG_MANAGER" "openssl"
            ;;
    esac

    # ------------------------------------------------------------------
    # 4. Установка Docker
    # ------------------------------------------------------------------
    install_docker "$DISTRO" "$PKG_MANAGER"

    # ------------------------------------------------------------------
    # 5. Проверка docker compose
    # ------------------------------------------------------------------
    if ! docker compose version >/dev/null 2>&1; then
        error "Docker Compose не доступен после установки Docker."
        exit 1
    fi
    log "Docker Compose: $(docker compose version --short 2>/dev/null || echo 'OK')"

    # ------------------------------------------------------------------
    # 6. Работа с репозиторием
    # ------------------------------------------------------------------
    APP_DIR="/opt/glass"
    REPO_URL="https://github.com/tvwoth/glass.git"
    REPO_BRANCH="${GLASS_BRANCH:-main}"

    if [[ -d "$APP_DIR/.git" ]]; then
        log "Репозиторий уже существует в $APP_DIR, обновляем..."
        cd "$APP_DIR"
        git fetch origin
        git checkout "$REPO_BRANCH" || true
        git pull --ff-only origin "$REPO_BRANCH" || true
    else
        log "Клонируем репозиторий в $APP_DIR..."
        rm -rf "$APP_DIR" 2>/dev/null || true
        git clone --branch "$REPO_BRANCH" --single-branch "$REPO_URL" "$APP_DIR"
        cd "$APP_DIR"
    fi

    log "Делаем скрипты исполняемыми..."
    chmod +x "$APP_DIR"/*.sh || true

    # ------------------------------------------------------------------
    # 7. Создание глобальных команд
    # ------------------------------------------------------------------
    log "Устанавливаем команды в /usr/local/bin..."
    mkdir -p /usr/local/bin
    ln -sf "$APP_DIR/install.sh"                /usr/local/bin/contour-install
    ln -sf "$APP_DIR/update.sh"                 /usr/local/bin/contour-update
    ln -sf "$APP_DIR/uninstall.sh"              /usr/local/bin/contour-uninstall
    ln -sf "$APP_DIR/change-admin-password.sh"  /usr/local/bin/contour-change-password
    ln -sf "$APP_DIR/reset-admin-password.sh"   /usr/local/bin/contour-reset-password
    success "Команды contour-* доступны глобально."

    # ------------------------------------------------------------------
    # 8. Запрос порта
    # ------------------------------------------------------------------
    read -rp "Введите порт приложения [5000]: " APP_PORT
    APP_PORT=${APP_PORT:-5000}
    while ! check_port "$APP_PORT"; do
        APP_PORT=$(prompt_port "$APP_PORT")
    done
    log "Порт приложения: $APP_PORT"

    # ------------------------------------------------------------------
    # 9. Создание/обновление .env
    # ------------------------------------------------------------------
    cd "$APP_DIR"

    if [[ ! -f .env ]]; then
        log "Создаём .env из шаблона..."
        if [[ -f .env.example ]]; then
            cp .env.example .env
        else
            echo "APP_PORT=${APP_PORT}" > .env
        fi
    fi

    # APP_PORT
    if grep -q '^APP_PORT=' .env 2>/dev/null; then
        sed -i "s/^APP_PORT=.*$/APP_PORT=${APP_PORT}/" .env
    else
        echo "APP_PORT=${APP_PORT}" >> .env
    fi

    # Пароль администратора
    if ! grep -q '^CONFIG_ADMIN_PASSWORD=' .env 2>/dev/null; then
        read -rsp "Введите пароль администратора (Enter = admin): " ADMIN_PW
        echo
        ADMIN_PW=${ADMIN_PW:-admin}
        echo "CONFIG_ADMIN_PASSWORD=${ADMIN_PW}" >> .env
        success "Пароль администратора установлен."
    else
        log "Пароль администратора уже задан в .env, пропускаем."
    fi

    # SECRET_KEY
    if ! grep -q '^SECRET_KEY=' .env 2>/dev/null; then
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
        echo "SECRET_KEY=${SECRET_KEY}" >> .env
        log "SECRET_KEY сгенерирован."
    fi

    # HOST_HTTP_PORT
    if ! grep -q '^HOST_HTTP_PORT=' .env 2>/dev/null; then
        echo "HOST_HTTP_PORT=80" >> .env
    fi

    # ------------------------------------------------------------------
    # 10. Создание каталогов и прав
    # ------------------------------------------------------------------
    mkdir -p "$APP_DIR/data/user_configs"
    chown -R 1000:1000 "$APP_DIR/data/user_configs" 2>/dev/null || true
    chmod 755 "$APP_DIR/data/user_configs" 2>/dev/null || true

    # ------------------------------------------------------------------
    # 11. Проверка порта для nginx
    # ------------------------------------------------------------------
    HOST_HTTP_PORT=$(grep '^HOST_HTTP_PORT=' .env | cut -d'=' -f2-)
    HOST_HTTP_PORT=${HOST_HTTP_PORT:-80}

    if is_port_busy "$HOST_HTTP_PORT"; then
        warn "Порт $HOST_HTTP_PORT занят на хосте."
        read -rp "Введите порт хоста для nginx [8080]: " HOST_HTTP_PORT
        HOST_HTTP_PORT=${HOST_HTTP_PORT:-8080}
        while is_port_busy "$HOST_HTTP_PORT"; do
            warn "Порт $HOST_HTTP_PORT тоже занят."
            read -rp "Введите порт хоста для nginx [8080]: " HOST_HTTP_PORT
            HOST_HTTP_PORT=${HOST_HTTP_PORT:-8080}
        done
    fi

    sed -i "s/^HOST_HTTP_PORT=.*$/HOST_HTTP_PORT=${HOST_HTTP_PORT}/" .env
    log "HTTP-порт nginx на хосте: ${HOST_HTTP_PORT}"

    # ------------------------------------------------------------------
    # 12. Запуск Docker-стека
    # ------------------------------------------------------------------
    log "Останавливаем существующие контейнеры..."
    docker compose down --remove-orphans 2>/dev/null || true

    log "Сборка и запуск контейнеров..."
    docker compose up -d --build --force-recreate

    # Ожидание запуска
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
            error "Контейнер не запустился. Логи:"
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
            warn "Контейнер запущен, но healthcheck не пройден. Логи:"
            docker logs --tail 20 glass 2>/dev/null || true
            break
        fi
    done

    # ------------------------------------------------------------------
    # 13. Автообновление (опционально)
    # ------------------------------------------------------------------
    if confirm "Включить ежедневное автообновление (systemd timer)?"; then
        log "Настраиваем systemd-таймеры..."
        cp "$APP_DIR/contour-update.service" "$APP_DIR/contour-update.timer" /etc/systemd/system/ 2>/dev/null || true
        systemctl daemon-reload
        systemctl enable --now contour-update.timer 2>/dev/null || true
        success "Автообновление включено."
    else
        log "Автообновление не включено."
    fi

    # ------------------------------------------------------------------
    # 14. Завершение
    # ------------------------------------------------------------------
    local ip
    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    ip=${ip:-<SERVER_IP>}

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  Установка завершена${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "  Адрес:    ${BLUE}http://${ip}:${HOST_HTTP_PORT}${NC}"
    echo ""
    echo -e "  Пароль администратора: ${YELLOW}(указан при установке)${NC}"
    echo ""
    echo -e "  Команды:"
    echo -e "    contour-install        — установка"
    echo -e "    contour-update         — обновление"
    echo -e "    contour-uninstall      — удаление"
    echo -e "    contour-change-password — смена пароля"
    echo -e "    contour-reset-password  — сброс пароля"
    echo ""
}

main "$@"