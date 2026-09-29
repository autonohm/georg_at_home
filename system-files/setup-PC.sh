readonly BOLD_MAGENTA=$'\033[7;95;1m'
readonly BOLD_GREEN=$'\033[7;92;1m'
readonly BOLD_YELLOW=$'\033[7;93;1m'
readonly BOLD_RED=$'\033[7;91;1m'
readonly RESET=$'\033[0m'
THIS_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

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

# (permissions, user, group, destination)
# source is assumed to be "./destination"
install_thingy() {
  if [ -e $4 ]; then
   log_warn "file '$4' already exists. Overwrite? (y/n)"
    read -r YN
  else
    YN="Y"
  fi
  if [ "$YN" = "y" ]||[ "$YN" = "Y" ]; then
    sudo install -D -m $1 -o $2 -g $3 "./$4" $4
    log_ok "Installed '$4'"
  fi
}


################################
###  BEGIN INSTALLING STUFF  ###
################################

printf "\nbeginning installation, stop at anytime with <control-c>\n\n"
sleep 1

log_state "udev rules"
install_thingy 644 root root "/etc/udev/rules.d/51-autonohm-joystick.rules"
sudo udevadm control --reload
sudo udevadm trigger

log_state "bashrc"
BASHRC="$HOME/.bashrc"
if grep -q "autonohm georg" $BASHRC ; then
  log_warn "bashrc at ${BASHRC}, already was modified. Skipping"
else
  echo -e "#autonohm georg setup\nsource ${THIS_SCRIPT_DIR}/projectctl-completion.bash" >> "$BASHRC"
  log_ok "bashrc at ${BASHRC}, modified."
fi

log_state "docker permissions"
# Give your user docker permissions
sudo usermod -aG docker "$USER"
newgrp docker # may need reboot to apply instead ot this