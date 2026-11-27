#!/bin/bash

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


log_state "apt install dependencies"
sudo apt update
sudo apt install hostapd chrony stress iperf3 tree lolcat nmap git gh btop htop can-utils -y

log_state "udev rules"
install_thingy 644 root root "/etc/udev/rules.d/51-autonohm-joystick.rules"
install_thingy 644 root root "/etc/udev/rules.d/99-pib-motors.rules"
sudo udevadm control --reload
sudo udevadm trigger

log_state "network config"
install_thingy 644 root root "/etc/NetworkManager/conf.d/00-georg.conf"
install_thingy 644 root root "/etc/systemd/network/10-create-bridge-br0.netdev"
install_thingy 644 root root "/etc/systemd/network/20-bind-ethernet-with-bridge-br0.network"
install_thingy 644 root root "/etc/systemd/network/30-config-bridge-br0.network"
#install_thingy 644 root root "/etc/systemd/network/80-can.network"
#install_thingy 600 root root "/etc/dnsmasq.d/00-georg.conf"
install_thingy 644 root root "/etc/systemd/system/georg-hostapd.service"
install_thingy 600 root root "/etc/hostapd/georg-AP.conf"

printf "${BOLD_GREEN}set wifi region? (y/n)${RESET}%s "
read -r YN
if [ "$YN" = "y" ]||[ "$YN" = "Y" ]; then
  RET=1
  while [ $RET != 0 ]; do
    log_ok "what region? (ISO/IEC 3166-1 alpha2, 2 char name)"
    read -r REG
    # We're running on raspi here, otherwise use `iw reg`
    sudo iw reg set "${REG}"
    #sudo iw reg set "${REG}"
    RET=$?
  done
  sudo iw reg get | grep country
fi

sudo systemctl daemon-reload
# enable network configs
sudo systemctl enable systemd-networkd
sudo systemctl start systemd-networkd
log_ok "enabled & started systemd-networkd"
# resolved clashes with dnsmasq
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
sudo systemctl mask systemd-resolved
sudo rm /etc/resolv.conf
sudo touch /etc/resolv.conf
# enable DHCP & DNS server
sudo systemctl enable dnsmasq &>/dev/null #STFU sysV
sudo systemctl start dnsmasq
log_ok "enabled & started dnsmasq"
# set up wifi AP
sudo systemctl unmask georg-hostapd.service
sudo systemctl enable georg-hostapd.service &>/dev/null #STFU sysV
sudo systemctl start georg-hostapd.service
log_ok "enabled wifi AP"


log_state "bashrc"
BASHRC="$HOME/.bashrc"
if grep -q "autonohm georg" $BASHRC ; then
  log_warn "bashrc at ${BASHRC}, already was modified. Skipping"
else
  echo -e "#autonohm georg setup\nsource ${THIS_SCRIPT_DIR}/projectctl-completion.bash" >> "$BASHRC"
  log_ok "bashrc at ${BASHRC}, modified."
fi

# https://docs.docker.com/engine/install/debian/
log_state "docker (docker-ce)"
if ! dpkg -s docker-ce &>/dev/null; then
  log_ok "installing docker-ce"

  sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-doc docker-buildx podman-docker containerd runc | cut -f1)

  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc

  # Add the repository to Apt sources:
  sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

  sudo apt update
  sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo systemctl start docker

  # Give your user docker permissions
  sudo usermod -aG docker "$USER"
  newgrp docker # may need reboot to apply instead ot this
else
  log_warn "docker-ce already installed. Skipping"
fi
