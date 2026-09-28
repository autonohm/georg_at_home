#!/bin/bash

GREEN='\033[1;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
THIS_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


# (permissions, user, group, destination)
# source is assumed to be "./destination"
install_thingy() {
  if [ -e $4 ]; then
    printf "${YELLOW}WARN: file '$4' already exists. Overwrite? (y/n) ${NC}"
    read -r YN
  else
    YN="Y"
  fi
  if [ "$YN" = "y" ]||[ "$YN" = "Y" ]; then
    sudo install -D -m $1 -o $2 -g $3 "./$4" $4
    printf "${GREEN}OK: Installed '$4${NC}' \n\n"
  fi
}

install_thingy 644 root root "/etc/udev/rules.d/51-autonohm-joystick.rules"
sudo udevadm control --reload
sudo udevadm trigger


BASHRC="$HOME/.bashrc"
if grep -q "autonohm georg" $BASHRC ; then
  printf "${YELLOW}WARN: bashrc at ${BASHRC}, already was modified. Skipping \n ${NC}"
else
  echo -e "#autonohm georg setup\nsource ${THIS_SCRIPT_DIR}/projectctl-completion.bash" >> "$BASHRC"
  printf "${GREEN}OK: bashrc at ${BASHRC}, modified. \n ${NC}"
fi
