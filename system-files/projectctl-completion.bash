_projectctl_completion() {
    local current previous
    local -a commands packages

    current=${COMP_WORDS[COMP_CWORD]}
    previous=${COMP_WORDS[COMP_CWORD - 1]:-}

    commands=(
        up
        down
        build
        start
        stop
        build_base_image
        logs
        mode
        check_pkgs
        install_completion
        help
    )

    if [[ "$COMP_CWORD" -eq 1 ]]; then
        COMPREPLY=(
            $(compgen -W "${commands[*]}" -- "$current")
        )
    elif [[ "$COMP_CWORD" -eq 2 ]] && [[ " up down build start stop " == *" $previous "* ]]; then
        COMPREPLY=(
            $(compgen -W "mock sim real mcap" -- "$current")
        )
    elif [[ "$COMP_CWORD" -ge 2 ]] && [[ ${COMP_WORDS[1]} == "logs" ]]; then
        mapfile -t packages < <(
            compgen -W "$(
                shopt -s nullglob
                for dir in packages/pkg_*/; do
                    dir=${dir%/}
                    dir=${dir##*/}
                    printf '%s\n' "${dir#pkg_}"
                done
            )" -- "$current"
        )
        COMPREPLY=("${packages[@]}")
    else
        COMPREPLY=()
    fi
}

complete -F _projectctl_completion projectctl.bash
complete -F _projectctl_completion /home/snaens/Code/AutonOhm/Georg/georg_at_home/projectctl.bash
complete -F _projectctl_completion ./projectctl.bash
