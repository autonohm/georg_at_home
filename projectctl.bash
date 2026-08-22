#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_NAME="georg"
PACKAGES_DIR="software"

# Space-separated package names to skip, for example:
SKIP_PACKAGES=("drive" "examples")
#SKIP_PACKAGES=( )

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
 	  if [[ "${SKIP_PACKAGES[*]}" == *"$1"* ]]; then # if array contains x
        return 0
    fi
    return 1
}

path_to_package_name() {
    local dir=$1  # software/pkg_xxx/
    dir=${dir%/}  # software/pkg_xxx
    dir=${dir##*/}  # pkg_xxx
    printf '%s\n' "${dir#pkg_}"  # xxx
}

check_packages() {
    local dir package skip
    local -a found_packages=()

    shopt -s nullglob
    for dir in "$PACKAGES_DIR"/pkg_*/; do
        package=$(path_to_package_name "$dir")
        found_packages+=("$package")
    done
    log_ok "found pkgs: ${found_packages[*]:-}"
    # :- expand to empty string if empty

    for skip in "${SKIP_PACKAGES[@]}"; do
        if [[ " ${found_packages[*]} " == *" $skip "* ]]; then
            log_warn "skipping pkg: $skip"
        else
            log_fatal "invalid skipee: $skip"
        fi
    done

    for dir in "$PACKAGES_DIR"/pkg_*/; do
        package=$(path_to_package_name "$dir")

        if is_skipped "$package"; then
            continue
        fi

        if [[ ! -f "$dir/docker-compose.yaml" ]]; then
            log_fatal "package $package missing docker-compose.yaml"
        fi

        if [[ ! -f "$dir/README.md" ]]; then
            log_warn "package $package missing README.md"
        fi
    done
}

build_base_image() {
    log_state "build georg-ros image"
    docker build -t georg-ros:humble software/docker_base_image/
}

docker_cmd() {
    local dir package


    for dir in "$PACKAGES_DIR"/pkg_*/; do
        package=$(path_to_package_name "$dir")

        if is_skipped "$package"; then
            continue
        fi

        log_state ">> $package"

        docker compose \
            -p "$PROJECT_NAME" \
            --progress plain \
            -f "${dir}docker-compose.yaml" \
            "$@"
    done
}

docker_logs() {
    selection=($*) # split along spaces

    for dir in "$PACKAGES_DIR"/pkg_*/; do
        package=$(path_to_package_name "$dir")
        packages+=($(path_to_package_name "$dir"))

        if is_skipped "$package"; then
            continue
        fi

        if [[ ${#selection[@]} == 1 ]] || [[ " ${selection[*]:1} " == *" $package "* ]]; then
            containers+=("${PROJECT_NAME}-${package}-1")
        fi
    done

    for sel in ${selection[*]:1}; do
      if [[ " ${packages[*]} " != *" $sel "* ]]; then
          log_warn "selection $sel is not a package"
      fi
    done
    docker logs --color --names --follow "${containers[@]%%/*}"
}

install_completion() {
  SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
  if grep -q "projectctl-completion.bash" "$HOME/.bashrc" ; then
      log_warn "Completion is already installed in bashrc. Skipping"
  else
      echo -e "\n# setup autocomplete for georg_at_home project control script\nsource $SCRIPT_DIR/software/projectctl-completion.bash" >> "$HOME/.bashrc"
      log_ok "Completion installed to $HOME/.bashrc. Run \`source $HOME/.bashrc\` or open a new terminal to apply"
  fi
}


usage() {
    cat <<'EOF'
Usage:
  projectctl [command]

Commands:
  up                  Check packages and bring up all containers (in background)
  down                Check packages and bring down all containers
  build               Check packages and build all containers
  build_base_image    Build base image used for software packages' containers
  start               Check packages and start all containers
  stop                Check packages and stop all containers
  logs [pkg_name]     View logs for specified Package (all if empty)
  check_pkgs          Validate packages (docker-compose.yaml present, README.md present)
  install_completion  Install autocompletion for this script (requires bash-completion)
  help                Show this help message
EOF
}

main() {
    local command=${1:-help}

    case "$command" in
        up)
            log_state "bringup containers"
            docker_cmd up -d 2>&1 | grep -Pv "orphan"
            # remove warning about orphan containers - always shows up due to project setup
            ;;
        down)
            log_state "bringdown containers"
            docker_cmd down
            ;;
        start)
            log_state "start containers"
            docker_cmd start
            ;;
        stop)
            check_packages
            log_state "stop containers"
            docker_cmd stop
            ;;
        build)
            check_packages
            build_base_image
            log_state "build containers"
            docker_cmd build
            ;;
        logs)
            docker_logs $@
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
