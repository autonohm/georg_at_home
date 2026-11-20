#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_NAME="georg"
PACKAGES_DIR="packages"
COMPOSE_FILE="compose.yaml"
MODE_FILE="/etc/georg/mode"
MODES=(mock sim real mcap)

# Space-separated package names to skip, for example:
#SKIP_PACKAGES=("drive" "examples")
SKIP_PACKAGES=( )

# --------------------------------------------------

readonly BOLD_MAGENTA=$'\033[7;95;1m'
readonly BOLD_GREEN=$'\033[7;92;1m'
readonly BOLD_YELLOW=$'\033[7;93;1m'
readonly BOLD_RED=$'\033[7;91;1m'
readonly RESET=$'\033[0m'

log_fatal() {
    printf '%s  %s  %s\n' "$BOLD_RED" "$1" "$RESET" >&2
    exit 1
}

log_warn() {
    printf '%s  %s  %s\n' "$BOLD_YELLOW" "$1" "$RESET" >&2
}

log_ok() {
    printf '%s  %s  %s\n' "$BOLD_GREEN" "$1" "$RESET"
}

log_state() {
    printf '%s  %s  %s\n' "$BOLD_MAGENTA" "$1" "$RESET"
}

is_skipped() {
	  if [[ "${SKIP_PACKAGES[*]:-}" == *"$1"* ]]; then # if array contains x
        return 0
    fi
    return 1
}

is_ignored() {
	  if [ -f "$PACKAGES_DIR/pkg_$1/PKG_IGNORE" ]; then # if file exists
        return 0
    fi
    return 1
}

path_to_package_name() {
    local dir=$1  # packages/pkg_xxx/
    dir=${dir%/}  # packages/pkg_xxx
    dir=${dir##*/}  # pkg_xxx
    printf '%s\n' "${dir#pkg_}"  # xxx
}

check_packages() {
    local dir package skip
    local -a found_packages=()

    shopt -s nullglob
    for dir in "$PACKAGES_DIR"/pkg_*/; do
        package=$(path_to_package_name "$dir")
        if is_ignored "$package"; then
            continue
        fi
        found_packages+=("$package")
    done
    log_ok "found pkgs: ${found_packages[*]:-}"
    # :- expand to empty string if empty

    for skip in ${SKIP_PACKAGES[@]+"${SKIP_PACKAGES[@]}"}; do
        if [[ " ${found_packages[*]} " == *" $skip "* ]]; then
            log_warn "skipping pkg: $skip"
        else
            log_fatal "invalid skipee: $skip"
        fi
    done

    for package in "${found_packages[@]}"; do
        if is_skipped "$package"; then
            continue
        fi

        if [[ ! -f "$PACKAGES_DIR/pkg_$package/docker-compose.yaml" ]]; then
            log_fatal "package $package missing docker-compose.yaml"
        fi

        if [[ ! -f "$PACKAGES_DIR/pkg_$package/README.md" ]]; then
            log_warn "package $package missing README.md"
        fi

        if ! grep -q "$PACKAGES_DIR/pkg_$package/docker-compose.yaml" "$COMPOSE_FILE"; then
            log_warn "package $package not included in $COMPOSE_FILE"
        fi
    done
}

build_base_image() {
    log_state "build georg-ros image"
    docker build -t georg-ros:jazzy \
        --build-context interfaces="$PACKAGES_DIR/pkg_interfaces" \
        "$PACKAGES_DIR/docker_base_image/"
}

device_mode() {
    # content of /etc/georg/mode, empty if missing
    if [[ -r "$MODE_FILE" ]]; then
        tr -d '[:space:]' < "$MODE_FILE"
    fi
}

check_mode() {
    local mode=$1
    if [[ " ${MODES[*]} " != *" $mode "* ]]; then
        log_fatal "unknown mode '$mode' (choose one of: ${MODES[*]})"
    fi
    if [[ "$mode" == "real" ]] && [[ "$(device_mode)" != "real" ]]; then
        log_fatal "mode 'real' refused: $MODE_FILE is '$(device_mode)', not 'real'. 'real' only runs on the robot."
    fi
}

compose() {
    # all compose calls go through the root compose file
    GEORG_DEVICE_MODE="$(device_mode)" \
        docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" "$@"
}

docker_cmd() {
    # run a compose command for one mode, or for all profiles if no mode is given
    local mode=$1
    shift
    if [[ -n "$mode" ]]; then
        check_mode "$mode"
        GEORG_PROFILE="$mode" compose --profile "$mode" "$@"
    else
        GEORG_PROFILE="" compose --profile '*' "$@"
    fi
}

docker_logs() {
    # logs [service ...]; service names are the package names (e.g. task_manager)
    compose --profile '*' logs --follow "$@"
}

install_completion() {
  SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
  if grep -q "projectctl-completion.bash" "$HOME/.bashrc" ; then
      log_warn "Completion is already installed in bashrc. Skipping"
  else
      echo -e "\n# setup autocomplete for georg_at_home project control script\nsource $SCRIPT_DIR/system-files/projectctl-completion.bash" >> "$HOME/.bashrc"
      log_ok "Completion installed to $HOME/.bashrc. Run \`source $HOME/.bashrc\` or open a new terminal to apply"
  fi
}


usage() {
    cat <<'USAGE'
Usage:
  projectctl [command]

Modes: mock | sim | real | mcap   ('real' only if /etc/georg/mode is 'real')

Commands:
  up <mode>           Check packages and bring up the containers of <mode> (in background)
  down [mode]         Bring down the containers of [mode] (all if empty)
  build [mode]        Check packages, build base image and the containers of [mode] (all if empty)
  build_base_image    Build base image used for software packages' containers
  start <mode>        Start the containers of <mode>
  stop [mode]         Stop the containers of [mode] (all if empty)
  logs [service ...]  View logs for the given services (all if empty)
  mode                Show the device mode from /etc/georg/mode
  check_pkgs          Validate packages (docker-compose.yaml, README.md, included in compose.yaml)
  install_completion  Install autocompletion for this script (requires bash-completion)
  help                Show this help message
USAGE
}

main() {
    local command=${1:-help}
    local mode=${2:-}

    case "$command" in
        up)
            [[ -n "$mode" ]] || log_fatal "up needs a mode: ${MODES[*]}"
            check_mode "$mode"
            check_packages
            log_state "bringup containers ($mode)"
            docker_cmd "$mode" up -d --remove-orphans
            ;;
        down)
            log_state "bringdown containers ${mode:-(all)}"
            docker_cmd "$mode" down
            ;;
        start)
            [[ -n "$mode" ]] || log_fatal "start needs a mode: ${MODES[*]}"
            log_state "start containers ($mode)"
            docker_cmd "$mode" start
            ;;
        stop)
            log_state "stop containers ${mode:-(all)}"
            docker_cmd "$mode" stop
            ;;
        build)
            [[ -z "$mode" ]] || check_mode "$mode"
            check_packages
            build_base_image
            log_state "build containers ${mode:-(all)}"
            docker_cmd "$mode" build
            ;;
        logs)
            shift
            docker_logs "$@"
            ;;
        mode)
            printf '%s\n' "$(device_mode)"
            ;;
        build_base_image|build-base-image)
            build_base_image
            ;;
        check_pkgs|check-pkgs)
            check_packages
            ;;
        install_completion|install-completion)
            install_completion
            ;;
        help|-h|--help)
            usage
            ;;
        *)
            printf 'Unknown command: %s\n\n' "$command" >&2
            usage >&2
            return 2
            ;;
    esac
}

main "$@"
