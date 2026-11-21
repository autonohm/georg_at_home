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

log_state "georg mode (plan P8)"
# a PC never runs profile 'real' (projectctl.bash refuses it)
sudo mkdir -p /etc/georg
echo sim | sudo tee /etc/georg/mode > /dev/null
log_ok "/etc/georg/mode = sim"

log_state "Lichtblick ${LICHTBLICK_VERSION:=1.30.0} (pinned, plan P4)"
if dpkg -s lichtblick &>/dev/null; then
  log_warn "Lichtblick already installed. Skipping"
else
  DEB="lichtblick-${LICHTBLICK_VERSION}-linux-$(dpkg --print-architecture).deb"
  curl -fsSL -o "/tmp/${DEB}" \
    "https://github.com/lichtblick-suite/lichtblick/releases/download/v${LICHTBLICK_VERSION}/${DEB}"
  sudo apt install -y "/tmp/${DEB}"
  log_ok "Lichtblick installed; panel: packages/pkg_viz/lichtblick_panel (python3 build.py)"
fi

log_state "Burr UI (plan P1)"
BURR_VENV="$HOME/.local/share/georg/burr-ui"
if [ ! -x "${BURR_VENV}/bin/python" ]; then
  python3 -m venv "${BURR_VENV}"
  "${BURR_VENV}/bin/pip" install --quiet "apache-burr[tracking]==0.43.0"
fi
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/georg-burr-ui" <<EOF
#!/usr/bin/env bash
# Burr UI on http://localhost:7241, reads ~/.burr (or BURR_DIR)
burr_path="\${BURR_DIR:-\$HOME/.burr}" exec "${BURR_VENV}/bin/python" -m uvicorn burr.tracking.server.run:app --port 7241
EOF
chmod +x "$HOME/.local/bin/georg-burr-ui"
log_ok "Burr UI: run georg-burr-ui"

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