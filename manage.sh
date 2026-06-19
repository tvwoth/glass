#!/usr/bin/env bash

################################################################################
#                                                                              #
#  manage.sh — управление Contour Glass                                       #
#                                                                              #
#  Использование:                                                              #
#    sudo ./manage.sh password     — смена пароля администратора               #
#                                                                              #
################################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()     { echo -e "${BLUE}[contour-manage]${NC} $*"; }
success() { echo -e "${GREEN}[contour-manage]${NC} $*"; }
error()   { echo -e "${RED}[contour-manage] ОШИБКА:${NC} $*" >&2; }

main() {
    if [[ $# -lt 1 ]]; then
        echo "Использование: sudo ./manage.sh <command>"
        echo ""
        echo "Команды:"
        echo "  password    Смена пароля администратора"
        exit 1
    fi

    local command="$1"
    shift

    case "$command" in
        password)
            exec "$(dirname "$0")/change-admin-password.sh" "$@"
            ;;
        *)
            error "Неизвестная команда: $command"
            echo "Доступные команды: password"
            exit 1
            ;;
    esac
}

main "$@"